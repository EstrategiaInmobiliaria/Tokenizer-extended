import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os
from pathlib import Path

class SocialMediaContentOptimizer:
    """
    Modelo: Optimizador de Contenido para Redes Sociales
    
    Entrada:
    - tipo_contenido: Carrusel, Reel, Story, Post (codificado)
    - hora_publicacion: Hora del día (0-23)
    - dia_semana: Día de la semana (0-6)
    - num_hashtags: Cantidad de hashtags (0-30)
    - tema_categoria: Categoría del tema (codificado)
    - longitud_caption: Longitud del caption (caracteres)
    
    Salida:
    - engagement_score: Score de engagement esperado (0-100)
    - probabilidad_viral: Probabilidad de volverse viral (0-1)
    - alcance_estimado: Alcance estimado (personas)
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.content_encoder = LabelEncoder()
        self.theme_encoder = LabelEncoder()
        self.model_path = Path(__file__).parent.parent / "models"
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    def build_model(self, input_shape):
        """Construye la arquitectura del modelo"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_shape,)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(3)  # [engagement_norm, prob_viral, alcance_norm]
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_data(self, df):
        """Prepara los datos para entrenamiento"""
        # Convertir fecha a features temporales
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['hora'] = df['fecha'].dt.hour
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        
        # Codificar tipo de contenido
        if not hasattr(self.content_encoder, 'classes_'):
            self.content_encoder.fit(df['tipo_contenido'])
        df['tipo_contenido_encoded'] = self.content_encoder.transform(df['tipo_contenido'])
        
        # Codificar tema
        if not hasattr(self.theme_encoder, 'classes_'):
            self.theme_encoder.fit(df['tema_categoria'])
        df['tema_encoded'] = self.theme_encoder.transform(df['tema_categoria'])
        
        # Calcular engagement score
        df['engagement_score'] = (
            df['likes'] * 1 + 
            df['guardados'] * 3 + 
            df['comentarios'] * 5 + 
            df['shares'] * 10
        ) / df['likes'].max()  # Normalizar
        
        # Features de entrada
        features = [
            'tipo_contenido_encoded', 'hora', 'dia_semana', 'es_fin_semana',
            'num_hashtags', 'tema_encoded', 'longitud_caption'
        ]
        
        X = df[features].values
        
        # Targets de salida
        y = np.column_stack([
            df['engagement_score'].values / 100,  # Normalizado
            (df['engagement_score'] > df['engagement_score'].quantile(0.8)).astype(int),  # Viral
            df['alcance'].values / df['alcance'].max()  # Normalizado
        ])
        
        return X, y, features
    
    def train(self, csv_path, epochs=100, validation_split=0.2):
        """Entrena el modelo con datos históricos de Instagram"""
        print("🔄 Cargando datos de Instagram...")
        df = pd.read_csv(csv_path)
        
        X, y, features = self.prepare_data(df)
        
        print(f"📊 Dataset: {len(df)} posts de Instagram")
        print(f"   Promedio likes: {df['likes'].mean():.0f}")
        print(f"   Promedio guardados: {df['guardados'].mean():.0f}")
        print(f"   Promedio comentarios: {df['comentarios'].mean():.0f}")
        
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
        
        # Callbacks
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Evaluar
        loss, mae = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"✅ Entrenamiento completado")
        print(f"   MAE: {mae:.4f}")
        
        # Guardar modelo en TensorFlow Lite
        self.save_tflite()
        
        # Guardar encoders y scaler
        joblib.dump(self.scaler, self.model_path / "social_media_scaler.pkl")
        joblib.dump(self.content_encoder, self.model_path / "content_encoder.pkl")
        joblib.dump(self.theme_encoder, self.model_path / "theme_encoder.pkl")
        
        return history
    
    def save_tflite(self):
        """Convierte y guarda modelo en formato TensorFlow Lite"""
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        
        tflite_path = self.model_path / "social_content_optimizer.tflite"
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"💾 Modelo guardado: {tflite_path}")
        print(f"   Tamaño: {len(tflite_model) / 1024:.1f} KB")
    
    def predict_week_schedule(self, temas_disponibles):
        """
        Genera calendario semanal óptimo de contenido
        
        Args:
            temas_disponibles: list de temas del Índice Maestro
            
        Returns:
            list de recomendaciones por día con mejor horario y formato
        """
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        tipos_contenido = ['Carrusel', 'Reel', 'Story', 'Post']
        
        schedule = []
        
        for dia_idx, dia_nombre in enumerate(dias):
            mejores_posts = []
            
            # Probar diferentes combinaciones
            for tema in temas_disponibles[:5]:  # Top 5 temas
                for tipo in tipos_contenido:
                    for hora in [9, 13, 18, 21]:  # Horarios clave
                        resultado = self.predict({
                            'tipo_contenido': tipo,
                            'hora': hora,
                            'dia_semana': dia_idx,
                            'num_hashtags': 5,
                            'tema_categoria': tema,
                            'longitud_caption': 150
                        })
                        
                        mejores_posts.append({
                            'tema': tema,
                            'tipo': tipo,
                            'hora': hora,
                            'engagement_esperado': resultado['engagement_score'],
                            'prob_viral': resultado['probabilidad_viral']
                        })
            
            # Tomar los 2 mejores posts del día
            mejores_posts.sort(key=lambda x: x['engagement_esperado'], reverse=True)
            schedule.append({
                'dia': dia_nombre,
                'posts': mejores_posts[:2]
            })
        
        return schedule
    
    def predict(self, post_data):
        """
        Predice performance para un post específico
        
        Args:
            post_data: dict con keys:
                - tipo_contenido: 'Carrusel', 'Reel', 'Story', 'Post'
                - hora: 0-23
                - dia_semana: 0-6
                - num_hashtags: cantidad
                - tema_categoria: tema del contenido
                - longitud_caption: caracteres
        
        Returns:
            dict con engagement_score, probabilidad_viral, alcance_estimado
        """
        # Cargar modelo TFLite
        interpreter = tf.lite.Interpreter(
            model_path=str(self.model_path / "social_content_optimizer.tflite")
        )
        interpreter.allocate_tensors()
        
        # Cargar encoders y scaler
        scaler = joblib.load(self.model_path / "social_media_scaler.pkl")
        content_encoder = joblib.load(self.model_path / "content_encoder.pkl")
        theme_encoder = joblib.load(self.model_path / "theme_encoder.pkl")
        
        # Preparar input
        es_fin_semana = 1 if post_data['dia_semana'] in [5, 6] else 0
        
        tipo_encoded = content_encoder.transform([post_data['tipo_contenido']])[0]
        tema_encoded = theme_encoder.transform([post_data['tema_categoria']])[0]
        
        X = np.array([[
            tipo_encoded,
            post_data['hora'],
            post_data['dia_semana'],
            es_fin_semana,
            post_data['num_hashtags'],
            tema_encoded,
            post_data['longitud_caption']
        ]], dtype=np.float32)
        
        X_scaled = scaler.transform(X).astype(np.float32)
        
        # Predecir
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], X_scaled)
        interpreter.invoke()
        
        output = interpreter.get_tensor(output_details[0]['index'])[0]
        
        return {
            'engagement_score': float(output[0] * 100),
            'probabilidad_viral': float(output[1]),
            'alcance_estimado': int(output[2] * 50000),  # Base de seguidores
            'recomendacion': 'PUBLICAR' if output[0] > 0.6 else 'OPTIMIZAR',
            'confianza': f"{output[1] * 100:.1f}%"
        }


def generate_sample_data(output_path):
    """Genera datos de ejemplo para entrenamiento inicial"""
    np.random.seed(42)
    
    tipos = ['Carrusel', 'Reel', 'Story', 'Post']
    temas = ['Cap Rate', 'Estrategia Inmobiliaria', 'Caso UIA', 'ExO', 
             'Productividad', 'Tenis', 'Familia', 'Inversiones']
    
    data = []
    base_date = pd.Timestamp('2024-01-01')
    
    for i in range(500):
        fecha = base_date + pd.Timedelta(days=np.random.randint(0, 365))
        tipo = np.random.choice(tipos, p=[0.25, 0.35, 0.25, 0.15])  # Reels más populares
        tema = np.random.choice(temas)
        hora = np.random.choice([7, 9, 12, 14, 18, 20, 21])
        num_hashtags = np.random.randint(2, 8)
        longitud = np.random.randint(50, 300)
        
        # Simular engagement basado en features
        base_engagement = {
            'Carrusel': 300,
            'Reel': 800,
            'Story': 150,
            'Post': 200
        }[tipo]
        
        # Boost por horario
        hora_boost = 1.5 if hora in [9, 18, 21] else 1.0
        
        # Boost por tema
        tema_boost = 1.3 if tema in ['Cap Rate', 'Estrategia Inmobiliaria'] else 1.0
        
        likes = int(base_engagement * hora_boost * tema_boost * np.random.uniform(0.7, 1.3))
        guardados = int(likes * np.random.uniform(0.05, 0.15))
        comentarios = int(likes * np.random.uniform(0.02, 0.08))
        shares = int(likes * np.random.uniform(0.01, 0.05))
        alcance = int(likes * np.random.uniform(3, 8))
        
        data.append({
            'fecha': fecha,
            'tipo_contenido': tipo,
            'tema_categoria': tema,
            'hora_publicacion': hora,
            'num_hashtags': num_hashtags,
            'longitud_caption': longitud,
            'likes': likes,
            'guardados': guardados,
            'comentarios': comentarios,
            'shares': shares,
            'alcance': alcance
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Datos de ejemplo generados: {output_path}")
    return df


if __name__ == "__main__":
    # Generar datos de ejemplo
    data_path = Path(__file__).parent.parent / "data" / "social_media"
    data_path.mkdir(parents=True, exist_ok=True)
    
    csv_path = data_path / "instagram_posts.csv"
    
    if not csv_path.exists():
        print("📝 Generando datos de ejemplo...")
        generate_sample_data(csv_path)
    
    # Entrenar modelo
    optimizer = SocialMediaContentOptimizer()
    optimizer.train(csv_path, epochs=100)
    
    # Probar predicción semanal
    print("\n🧪 Generando calendario semanal óptimo...")
    temas = ['Cap Rate', 'Estrategia Inmobiliaria', 'Caso UIA', 'ExO', 'Tenis']
    schedule = optimizer.predict_week_schedule(temas)
    
    print("\n📅 CALENDARIO SEMANAL RECOMENDADO:")
    for dia_info in schedule[:3]:  # Mostrar solo 3 días
        print(f"\n{dia_info['dia']}:")
        for post in dia_info['posts']:
            print(f"  📱 {post['hora']:02d}:00 - {post['tipo']} sobre '{post['tema']}'")
            print(f"     Engagement esperado: {post['engagement_esperado']:.1f}/100")
            print(f"     Prob. viral: {post['prob_viral']*100:.1f}%")
