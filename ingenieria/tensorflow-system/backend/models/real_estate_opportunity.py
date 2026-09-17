import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pathlib import Path

class RealEstateOpportunityDetector:
    """
    Modelo: Detector de Oportunidades Inmobiliarias
    
    Entrada:
    - precio_m2: Precio por metro cuadrado
    - ubicacion_encoded: Ubicación codificada (0-100)
    - amenidades: Cantidad de amenidades (0-20)
    - velocidad_ventas: Velocidad de ventas (0-1)
    - cap_rate: Tasa de capitalización (%)
    
    Salida:
    - probabilidad_venta_12m: Probabilidad de venta en 12 meses (0-1)
    - precio_estimado: Precio de venta estimado
    - dias_estimados: Días estimados para venta
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path(__file__).parent.parent / "models"
        self.model_path.mkdir(parents=True, exist_ok=True)
        
    def build_model(self, input_shape):
        """Construye la arquitectura del modelo"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_shape,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3, activation='sigmoid')  # [prob_venta, precio_norm, dias_norm]
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def prepare_data(self, df):
        """Prepara los datos para entrenamiento"""
        # Codificar ubicaciones
        location_mapping = {
            'Querétaro': 85, 'CDMX': 90, 'Monterrey': 88,
            'Guadalajara': 82, 'Mérida': 75, 'Cancún': 80,
            'Puebla': 70, 'Toluca': 65, 'León': 60
        }
        
        df['ubicacion_encoded'] = df['ubicacion'].map(location_mapping).fillna(50)
        
        # Features de entrada
        features = ['precio_m2', 'ubicacion_encoded', 'amenidades', 
                   'velocidad_ventas', 'cap_rate']
        X = df[features].values
        
        # Targets de salida (normalizados)
        y = np.column_stack([
            df['vendido_12_meses'].values,  # 0 o 1
            df['precio_venta_real'].values / 100000000,  # Normalizado a millones
            df['dias_venta'].values / 365  # Normalizado a años
        ])
        
        return X, y, features
    
    def train(self, csv_path, epochs=100, validation_split=0.2):
        """Entrena el modelo con datos históricos"""
        print("🔄 Cargando datos de entrenamiento...")
        df = pd.read_csv(csv_path)
        
        X, y, features = self.prepare_data(df)
        
        print(f"📊 Dataset: {len(df)} desarrollos inmobiliarios")
        print(f"   Vendidos en 12m: {df['vendido_12_meses'].sum()}")
        print(f"   No vendidos: {len(df) - df['vendido_12_meses'].sum()}")
        
        # Escalar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=validation_split, random_state=42
        )
        
        # Construir y entrenar modelo
        print("🧠 Construyendo red neuronal...")
        self.model = self.build_model(X_train.shape[1])
        
        print("🏋️  Entrenando modelo...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=16,
            verbose=0
        )
        
        # Evaluar
        loss, mae, mse = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"✅ Entrenamiento completado")
        print(f"   MAE: {mae:.4f}")
        print(f"   MSE: {mse:.4f}")
        
        # Guardar modelo en TensorFlow Lite
        self.save_tflite()
        
        # Guardar scaler
        joblib.dump(self.scaler, self.model_path / "real_estate_scaler.pkl")
        
        return history
    
    def save_tflite(self):
        """Convierte y guarda modelo en formato TensorFlow Lite"""
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
        tflite_path = self.model_path / "real_estate_opportunity.tflite"
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"💾 Modelo guardado: {tflite_path}")
        print(f"   Tamaño: {len(tflite_model) / 1024:.1f} KB")
    
    def predict(self, desarrollo_data):
        """
        Predice oportunidad para un desarrollo
        
        Args:
            desarrollo_data: dict con keys:
                - precio_m2
                - ubicacion
                - amenidades
                - velocidad_ventas
                - cap_rate
        
        Returns:
            dict con probabilidad_venta_12m, precio_estimado, dias_estimados
        """
        # Cargar modelo TFLite
        interpreter = tf.lite.Interpreter(
            model_path=str(self.model_path / "real_estate_opportunity.tflite")
        )
        interpreter.allocate_tensors()
        
        # Cargar scaler
        scaler = joblib.load(self.model_path / "real_estate_scaler.pkl")
        
        # Preparar input
        location_mapping = {
            'Querétaro': 85, 'CDMX': 90, 'Monterrey': 88,
            'Guadalajara': 82, 'Mérida': 75, 'Cancún': 80,
            'Puebla': 70, 'Toluca': 65, 'León': 60
        }
        
        ubicacion_encoded = location_mapping.get(desarrollo_data['ubicacion'], 50)
        
        X = np.array([[
            desarrollo_data['precio_m2'],
            ubicacion_encoded,
            desarrollo_data['amenidades'],
            desarrollo_data['velocidad_ventas'],
            desarrollo_data['cap_rate']
        ]], dtype=np.float32)
        
        X_scaled = scaler.transform(X).astype(np.float32)
        
        # Predecir
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], X_scaled)
        interpreter.invoke()
        
        output = interpreter.get_tensor(output_details[0]['index'])[0]
        
        return {
            'probabilidad_venta_12m': float(output[0]),
            'precio_estimado': float(output[1] * 100000000),  # Desnormalizar
            'dias_estimados': int(output[2] * 365),
            'recomendacion': 'ALTA PRIORIDAD' if output[0] > 0.7 else 'ANALIZAR' if output[0] > 0.4 else 'BAJA PRIORIDAD',
            'certeza': f"{output[0] * 100:.1f}%"
        }


def generate_sample_data(output_path):
    """Genera datos de ejemplo para entrenamiento inicial"""
    np.random.seed(42)
    
    ubicaciones = ['Querétaro', 'CDMX', 'Monterrey', 'Guadalajara', 'Mérida', 
                   'Cancún', 'Puebla', 'Toluca', 'León']
    
    data = []
    for i in range(200):
        ubicacion = np.random.choice(ubicaciones)
        precio_m2 = np.random.uniform(25000, 75000)
        amenidades = np.random.randint(3, 18)
        velocidad_ventas = np.random.uniform(0.3, 0.95)
        cap_rate = np.random.uniform(4.5, 9.5)
        
        # Lógica de probabilidad de venta (basada en features)
        score = (
            (1 - (precio_m2 - 25000) / 50000) * 0.3 +  # Precio más bajo = mejor
            (amenidades / 18) * 0.2 +  # Más amenidades = mejor
            velocidad_ventas * 0.3 +  # Mayor velocidad = mejor
            (cap_rate / 9.5) * 0.2  # Mayor cap rate = mejor
        )
        
        vendido = 1 if score > 0.6 else 0
        precio_venta = precio_m2 * np.random.uniform(800, 2500) * (1 if vendido else 0.85)
        dias_venta = int(np.random.uniform(90, 365) if vendido else np.random.uniform(300, 730))
        
        data.append({
            'desarrollo': f'DEV-{i+1:03d}',
            'precio_m2': precio_m2,
            'ubicacion': ubicacion,
            'amenidades': amenidades,
            'velocidad_ventas': velocidad_ventas,
            'cap_rate': cap_rate,
            'vendido_12_meses': vendido,
            'precio_venta_real': precio_venta,
            'dias_venta': dias_venta
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Datos de ejemplo generados: {output_path}")
    return df


if __name__ == "__main__":
    # Generar datos de ejemplo
    data_path = Path(__file__).parent.parent / "data" / "real_estate"
    data_path.mkdir(parents=True, exist_ok=True)
    
    csv_path = data_path / "training_data.csv"
    
    if not csv_path.exists():
        print("📝 Generando datos de ejemplo...")
        generate_sample_data(csv_path)
    
    # Entrenar modelo
    detector = RealEstateOpportunityDetector()
    detector.train(csv_path, epochs=150)
    
    # Probar predicción
    print("\n🧪 Probando predicción...")
    test_desarrollo = {
        'precio_m2': 45000,
        'ubicacion': 'Querétaro',
        'amenidades': 12,
        'velocidad_ventas': 0.85,
        'cap_rate': 7.2
    }
    
    resultado = detector.predict(test_desarrollo)
    print(f"\n📊 Resultado para desarrollo de prueba:")
    print(f"   Ubicación: {test_desarrollo['ubicacion']}")
    print(f"   Precio m2: ${test_desarrollo['precio_m2']:,.0f}")
    print(f"   Cap Rate: {test_desarrollo['cap_rate']}%")
    print(f"\n   ✨ Probabilidad de venta: {resultado['certeza']}")
    print(f"   💰 Precio estimado: ${resultado['precio_estimado']:,.0f}")
    print(f"   📅 Días estimados: {resultado['dias_estimados']}")
    print(f"   🎯 Recomendación: {resultado['recomendacion']}")
