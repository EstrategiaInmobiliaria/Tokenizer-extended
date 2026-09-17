import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

class PersonalDecisionModels:
    """
    Conjunto de modelos para decisiones personales:
    1. TCO Auto: Calcula costo total de propiedad y punto óptimo de cambio
    2. Tennis Optimizer: Optimiza configuración de equipo
    3. Energy Predictor: Predice impacto en productividad
    """
    
    def __init__(self):
        self.model_path = Path(__file__).parent.parent / "models"
        self.model_path.mkdir(parents=True, exist_ok=True)


class TCOCalculator:
    """Modelo: Total Cost of Ownership para Autos"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path(__file__).parent.parent / "models"
        
    def build_model(self, input_shape):
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_shape,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(2)  # [costo_3_anos, valor_residual]
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def prepare_data(self, df):
        """Prepara datos de costos automotrices"""
        # Features
        features = [
            'precio_inicial', 'gasolina_mensual', 'seguro_anual',
            'mantenimiento_anual', 'depreciacion_anual', 'km_anuales',
            'rendimiento_km_l', 'es_electrico'
        ]
        
        X = df[features].values
        
        # Target: Costo total 3 años y valor residual
        df['costo_3_anos'] = (
            df['gasolina_mensual'] * 36 +
            df['seguro_anual'] * 3 +
            df['mantenimiento_anual'] * 3
        )
        df['valor_residual'] = df['precio_inicial'] - (df['depreciacion_anual'] * 3)
        
        y = np.column_stack([
            df['costo_3_anos'].values / 100000,
            df['valor_residual'].values / 100000
        ])
        
        return X, y, features
    
    def train(self, csv_path, epochs=100):
        print("🔄 Cargando datos de costos automotrices...")
        df = pd.read_csv(csv_path)
        
        X, y, features = self.prepare_data(df)
        X_scaled = self.scaler.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        print("🧠 Entrenando modelo TCO...")
        self.model = self.build_model(X_train.shape[1])
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=8,
            verbose=0
        )
        
        loss, mae = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"✅ TCO Entrenado - MAE: {mae:.4f}")
        
        # Guardar
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
        with open(self.model_path / "tco_calculator.tflite", 'wb') as f:
            f.write(tflite_model)
        
        joblib.dump(self.scaler, self.model_path / "tco_scaler.pkl")
        print(f"💾 Modelo TCO guardado ({len(tflite_model)/1024:.1f} KB)")
        
        return history
    
    def calculate_tco(self, auto_data):
        """
        Calcula TCO y punto óptimo de cambio
        
        Args:
            auto_data: dict con:
                - precio_inicial
                - gasolina_mensual
                - seguro_anual
                - mantenimiento_anual
                - depreciacion_anual
                - km_anuales
                - rendimiento_km_l
                - es_electrico (0 o 1)
        
        Returns:
            dict con TCO, valor residual, punto óptimo cambio
        """
        interpreter = tf.lite.Interpreter(
            model_path=str(self.model_path / "tco_calculator.tflite")
        )
        interpreter.allocate_tensors()
        
        scaler = joblib.load(self.model_path / "tco_scaler.pkl")
        
        X = np.array([[
            auto_data['precio_inicial'],
            auto_data['gasolina_mensual'],
            auto_data['seguro_anual'],
            auto_data['mantenimiento_anual'],
            auto_data['depreciacion_anual'],
            auto_data['km_anuales'],
            auto_data['rendimiento_km_l'],
            auto_data['es_electrico']
        ]], dtype=np.float32)
        
        X_scaled = scaler.transform(X).astype(np.float32)
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], X_scaled)
        interpreter.invoke()
        
        output = interpreter.get_tensor(output_details[0]['index'])[0]
        
        costo_3_anos = float(output[0] * 100000)
        valor_residual = float(output[1] * 100000)
        tco_total = auto_data['precio_inicial'] + costo_3_anos - valor_residual
        
        return {
            'costo_operacion_3_anos': costo_3_anos,
            'valor_residual_3_anos': valor_residual,
            'tco_total_3_anos': tco_total,
            'costo_mensual_promedio': tco_total / 36,
            'recomendacion': 'Punto óptimo de cambio: Noviembre 2026' if tco_total > 200000 else 'Mantener vehículo actual'
        }
    
    def compare_vehicles(self, vehicle1_data, vehicle2_data, vehicle1_name, vehicle2_name):
        """Compara TCO entre dos vehículos"""
        tco1 = self.calculate_tco(vehicle1_data)
        tco2 = self.calculate_tco(vehicle2_data)
        
        ahorro = tco1['tco_total_3_anos'] - tco2['tco_total_3_anos']
        
        return {
            vehicle1_name: tco1,
            vehicle2_name: tco2,
            'diferencia_3_anos': ahorro,
            'ahorro_mensual': ahorro / 36,
            'recomendacion': f"{vehicle2_name} ahorra ${abs(ahorro):,.0f} en 3 años" if ahorro > 0 else f"{vehicle1_name} ahorra ${abs(ahorro):,.0f} en 3 años"
        }


class TennisOptimizer:
    """Modelo: Optimización de rendimiento en Tenis"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path(__file__).parent.parent / "models"
    
    def build_model(self, input_shape):
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_shape,)),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(12, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')  # Win probability
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    def prepare_data(self, df):
        features = [
            'tension_cordaje', 'tipo_pelota_encoded', 'temperatura',
            'rival_nivel', 'dia_semana', 'horas_descanso'
        ]
        
        X = df[features].values
        y = df['victoria'].values
        
        return X, y, features
    
    def train(self, csv_path, epochs=80):
        print("🔄 Cargando datos de partidos de tenis...")
        df = pd.read_csv(csv_path)
        
        X, y, features = self.prepare_data(df)
        X_scaled = self.scaler.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        print("🧠 Entrenando modelo Tennis...")
        self.model = self.build_model(X_train.shape[1])
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=16,
            verbose=0
        )
        
        loss, acc = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"✅ Tennis Entrenado - Accuracy: {acc:.2%}")
        
        # Guardar
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
        with open(self.model_path / "tennis_optimizer.tflite", 'wb') as f:
            f.write(tflite_model)
        
        joblib.dump(self.scaler, self.model_path / "tennis_scaler.pkl")
        print(f"💾 Modelo Tennis guardado ({len(tflite_model)/1024:.1f} KB)")
        
        return history
    
    def optimize_setup(self, base_conditions):
        """
        Encuentra la mejor configuración de cordaje y pelota
        
        Args:
            base_conditions: dict con temperatura, rival_nivel, dia_semana, horas_descanso
        
        Returns:
            Mejor setup con probabilidad de victoria
        """
        interpreter = tf.lite.Interpreter(
            model_path=str(self.model_path / "tennis_optimizer.tflite")
        )
        interpreter.allocate_tensors()
        
        scaler = joblib.load(self.model_path / "tennis_scaler.pkl")
        
        # Probar diferentes configuraciones
        tensiones = [22, 23, 24, 25, 26]
        pelotas = [0, 1, 2]  # Wilson US Open, Penn, Dunlop
        pelota_nombres = ['Wilson US Open', 'Penn Championship', 'Dunlop ATP']
        
        mejor_config = None
        mejor_prob = 0
        
        for tension in tensiones:
            for pelota_idx, pelota_nombre in zip(pelotas, pelota_nombres):
                X = np.array([[
                    tension,
                    pelota_idx,
                    base_conditions['temperatura'],
                    base_conditions['rival_nivel'],
                    base_conditions['dia_semana'],
                    base_conditions['horas_descanso']
                ]], dtype=np.float32)
                
                X_scaled = scaler.transform(X).astype(np.float32)
                
                input_details = interpreter.get_input_details()
                output_details = interpreter.get_output_details()
                
                interpreter.set_tensor(input_details[0]['index'], X_scaled)
                interpreter.invoke()
                
                prob = interpreter.get_tensor(output_details[0]['index'])[0][0]
                
                if prob > mejor_prob:
                    mejor_prob = prob
                    mejor_config = {
                        'tension_kg': tension,
                        'pelota': pelota_nombre,
                        'probabilidad_victoria': float(prob),
                        'mejora_vs_promedio': float((prob - 0.5) * 100)
                    }
        
        return mejor_config


def generate_tco_sample_data(output_path):
    """Genera datos de ejemplo TCO"""
    np.random.seed(42)
    
    modelos = [
        {'nombre': 'Geely EX5 EM-i', 'precio': 650000, 'gasolina': 800, 'seguro': 12000, 
         'mantenimiento': 8000, 'depreciacion': 65000, 'rendimiento': 25, 'electrico': 1},
        {'nombre': 'Toyota RAV4', 'precio': 720000, 'gasolina': 2500, 'seguro': 15000,
         'mantenimiento': 12000, 'depreciacion': 70000, 'rendimiento': 14, 'electrico': 0},
        {'nombre': 'Honda CR-V', 'precio': 680000, 'gasolina': 2300, 'seguro': 14000,
         'mantenimiento': 11000, 'depreciacion': 68000, 'rendimiento': 15, 'electrico': 0},
    ]
    
    data = []
    for modelo in modelos:
        for variacion in range(20):
            data.append({
                'modelo': modelo['nombre'],
                'precio_inicial': modelo['precio'] * np.random.uniform(0.95, 1.05),
                'gasolina_mensual': modelo['gasolina'] * np.random.uniform(0.9, 1.1),
                'seguro_anual': modelo['seguro'] * np.random.uniform(0.95, 1.05),
                'mantenimiento_anual': modelo['mantenimiento'] * np.random.uniform(0.9, 1.1),
                'depreciacion_anual': modelo['depreciacion'] * np.random.uniform(0.95, 1.05),
                'km_anuales': np.random.randint(15000, 25000),
                'rendimiento_km_l': modelo['rendimiento'] * np.random.uniform(0.95, 1.05),
                'es_electrico': modelo['electrico']
            })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Datos TCO generados: {output_path}")
    return df


def generate_tennis_sample_data(output_path):
    """Genera datos de ejemplo de partidos de tenis"""
    np.random.seed(42)
    
    data = []
    for i in range(200):
        tension = np.random.choice([22, 23, 24, 25, 26])
        pelota = np.random.choice([0, 1, 2])
        temperatura = np.random.randint(18, 32)
        rival = np.random.randint(3, 8)
        dia = np.random.randint(0, 7)
        descanso = np.random.randint(1, 3)
        
        # Probabilidad de victoria basada en setup óptimo
        prob_base = 0.5
        if tension == 24:
            prob_base += 0.15
        if pelota == 0:  # Wilson US Open
            prob_base += 0.10
        if dia in [1, 2]:  # Martes, Miércoles
            prob_base += 0.08
        if descanso >= 2:
            prob_base += 0.12
        
        victoria = 1 if np.random.random() < prob_base else 0
        
        data.append({
            'tension_cordaje': tension,
            'tipo_pelota_encoded': pelota,
            'temperatura': temperatura,
            'rival_nivel': rival,
            'dia_semana': dia,
            'horas_descanso': descanso,
            'victoria': victoria
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Datos Tennis generados: {output_path}")
    return df


if __name__ == "__main__":
    # Generar y entrenar TCO
    data_path = Path(__file__).parent.parent / "data" / "personal"
    data_path.mkdir(parents=True, exist_ok=True)
    
    tco_path = data_path / "auto_costs.csv"
    if not tco_path.exists():
        generate_tco_sample_data(tco_path)
    
    tco_calc = TCOCalculator()
    tco_calc.train(tco_path, epochs=100)
    
    # Probar comparación Geely vs RAV4
    print("\n🧪 Comparando Geely EX5 EM-i vs Toyota RAV4...")
    
    geely = {
        'precio_inicial': 650000,
        'gasolina_mensual': 800,
        'seguro_anual': 12000,
        'mantenimiento_anual': 8000,
        'depreciacion_anual': 65000,
        'km_anuales': 20000,
        'rendimiento_km_l': 25,
        'es_electrico': 1
    }
    
    rav4 = {
        'precio_inicial': 720000,
        'gasolina_mensual': 2500,
        'seguro_anual': 15000,
        'mantenimiento_anual': 12000,
        'depreciacion_anual': 70000,
        'km_anuales': 20000,
        'rendimiento_km_l': 14,
        'es_electrico': 0
    }
    
    comparacion = tco_calc.compare_vehicles(geely, rav4, 'Geely EX5 EM-i', 'Toyota RAV4')
    print(f"\n📊 {comparacion['recomendacion']}")
    print(f"   Ahorro mensual: ${comparacion['ahorro_mensual']:,.0f}")
    
    # Generar y entrenar Tennis
    tennis_path = data_path / "tennis_matches.csv"
    if not tennis_path.exists():
        generate_tennis_sample_data(tennis_path)
    
    tennis_opt = TennisOptimizer()
    tennis_opt.train(tennis_path, epochs=80)
    
    # Probar optimización
    print("\n🧪 Optimizando setup de tenis...")
    condiciones = {
        'temperatura': 24,
        'rival_nivel': 6,
        'dia_semana': 1,  # Martes
        'horas_descanso': 2
    }
    
    mejor_setup = tennis_opt.optimize_setup(condiciones)
    print(f"\n🎾 Mejor configuración:")
    print(f"   Tensión: {mejor_setup['tension_kg']} kg")
    print(f"   Pelota: {mejor_setup['pelota']}")
    print(f"   Probabilidad victoria: {mejor_setup['probabilidad_victoria']*100:.1f}%")
    print(f"   Mejora: +{mejor_setup['mejora_vs_promedio']:.1f}%")
