#!/usr/bin/env python3
"""
Gemelo Digital "Nivel LeyENDA"

Characteristics
---------------
- Subscribes to MQTT topics published by real or simulated sensors.
- Trains lightweight LSTM models per-sensor for short-term forecasting.
- Visualizes sensor state and predictions with a Dash + Plotly dashboard.

Run:
    pip install -r requirements (see README section)
    python gemelo_legendario.py
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import dash
import numpy as np
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
from dash import Input, Output, dcc, html
from sklearn.preprocessing import MinMaxScaler

# Silence TensorFlow's excessive logging before it loads any kernels.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
LOGGER = logging.getLogger("GemeloLegendario")


# ------------------------- CONFIGURACIÓN GLOBAL ------------------------- #
MQTT_BROKER = os.environ.get("GEMELO_MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.environ.get("GEMELO_MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("GEMELO_MQTT_TOPIC", "jaime/planta/#")

LOOK_BACK = int(os.environ.get("GEMELO_LOOK_BACK", "10"))
BUFFER_SIZE = int(os.environ.get("GEMELO_BUFFER_SIZE", "200"))

TRAINING_INTERVAL_SECONDS = int(os.environ.get("GEMELO_TRAIN_INTERVAL", "10"))
SIMULATION_INTERVAL_SECONDS = float(os.environ.get("GEMELO_SIM_INTERVAL", "1.0"))

DASH_PORT = int(os.environ.get("GEMELO_DASH_PORT", "8055"))
DASH_HOST = os.environ.get("GEMELO_DASH_HOST", "0.0.0.0")


# ------------------------------ SENSOR DATA ----------------------------- #
class SensorData:
    """Hold readings + ML state for a single sensor."""

    def __init__(self, name: str, position: Tuple[float, float, float]):
        self.name = name
        self.pos = position
        self.values: List[float] = []
        self.timestamps: List[datetime] = []

        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model: Optional[Sequential] = None
        self.is_trained = False
        self._lock = threading.Lock()

    # ----------------------- DATA INGESTION ----------------------- #
    def add_reading(self, value: float) -> None:
        with self._lock:
            self.values.append(float(value))
            self.timestamps.append(datetime.now())

            if len(self.values) > BUFFER_SIZE:
                self.values.pop(0)
                self.timestamps.pop(0)

    # -------------------------- TRAINING -------------------------- #
    def train_lstm(self) -> None:
        with self._lock:
            if len(self.values) < max(LOOK_BACK + 1, BUFFER_SIZE // 2):
                return

            data_array = np.array(self.values).reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(data_array)

            inputs, targets = [], []
            for idx in range(len(scaled_data) - LOOK_BACK - 1):
                inputs.append(scaled_data[idx : idx + LOOK_BACK, 0])
                targets.append(scaled_data[idx + LOOK_BACK, 0])

            if not inputs:
                return

            X = np.array(inputs).reshape(-1, LOOK_BACK, 1)
            y = np.array(targets)

        # Model can be trained outside the lock.
        model = Sequential(
            [
                LSTM(30, activation="relu", input_shape=(LOOK_BACK, 1)),
                Dense(1),
            ]
        )
        model.compile(loss="mean_squared_error", optimizer="adam")
        model.fit(X, y, epochs=5, batch_size=16, verbose=0)

        with self._lock:
            self.model = model
            self.is_trained = True
            LOGGER.info("🧠 Modelo LSTM entrenado para %s", self.name)

    # -------------------------- PREDICTION ------------------------- #
    def predict_next(self) -> Optional[float]:
        with self._lock:
            if not self.is_trained or len(self.values) < LOOK_BACK:
                return None

            last_seq = np.array(self.values[-LOOK_BACK:]).reshape(-1, 1)
            scaled_seq = self.scaler.transform(last_seq)

        predicted = self.model.predict(
            scaled_seq.reshape(1, LOOK_BACK, 1),
            verbose=0,
        )

        with self._lock:
            return float(self.scaler.inverse_transform(predicted)[0][0])

    def latest_value(self) -> Optional[float]:
        with self._lock:
            if not self.values:
                return None
            return self.values[-1]

    def recent_values(self, count: int = 30) -> List[float]:
        with self._lock:
            return self.values[-count:]


# ---------------------------- SENSOR REGISTRY --------------------------- #
SENSORS: Dict[str, SensorData] = {
    "Motor_Temp": SensorData("Motor_Temp", (0.0, 0.0, 0.0)),
    "Motor_Vib": SensorData("Motor_Vib", (1.0, 0.0, 0.0)),
    "Ambiente": SensorData("Ambiente", (0.0, 2.0, 1.0)),
}


# ----------------------------- MQTT INGESTION --------------------------- #
def _handle_payload(payload: Dict[str, float]) -> None:
    if "temp" in payload and "Motor_Temp" in SENSORS:
        SENSORS["Motor_Temp"].add_reading(payload["temp"])
    if "vib" in payload and "Motor_Vib" in SENSORS:
        SENSORS["Motor_Vib"].add_reading(payload["vib"])
    if "amb" in payload and "Ambiente" in SENSORS:
        SENSORS["Ambiente"].add_reading(payload["amb"])


def on_message(client: mqtt.Client, user_data, message: mqtt.MQTTMessage) -> None:
    try:
        payload = json.loads(message.payload.decode())
        _handle_payload(payload)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Error parsing MQTT payload: %s", exc)


def mqtt_worker() -> None:
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.subscribe(MQTT_TOPIC)
    LOGGER.info("Escuchando MQTT en %s:%s topic %s", MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    client.loop_forever()


# ------------------------------ SIMULADOR ------------------------------- #
def simulator_worker() -> None:
    LOGGER.info("Iniciando simulador de respaldo (desactivar con GEMELO_SIM_INTERVAL=0)")
    while SIMULATION_INTERVAL_SECONDS > 0:
        now = time.time()
        ambient_val = 22 + 2 * np.sin(now / 5) + np.random.normal(0, 0.2)
        SENSORS["Ambiente"].add_reading(ambient_val)

        if not SENSORS["Motor_Temp"].values:
            temp_val = 40 + 5 * np.sin(now / 10) + np.random.normal(0, 0.3)
            SENSORS["Motor_Temp"].add_reading(temp_val)

        if not SENSORS["Motor_Vib"].values:
            vib_val = 0.25 + 0.05 * np.sin(now / 3) + np.random.normal(0, 0.02)
            SENSORS["Motor_Vib"].add_reading(vib_val)

        time.sleep(SIMULATION_INTERVAL_SECONDS)


# ------------------------------ TRAINER LOOP ---------------------------- #
def trainer_worker() -> None:
    while True:
        time.sleep(TRAINING_INTERVAL_SECONDS)
        for sensor in SENSORS.values():
            if not sensor.is_trained:
                sensor.train_lstm()


# ------------------------------ DASH APP -------------------------------- #
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("🏭 Gemelo Digital: Nivel LEYENDA (MQTT + LSTM)", style={"textAlign": "center"}),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Visualización Espacial 3D"),
                        dcc.Graph(id="3d-view"),
                    ],
                    style={"width": "60%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.H3("Predicción IA (Próximo Step)"),
                        dcc.Graph(id="ai-graph"),
                        html.Div(id="alert-box", style={"color": "red", "fontWeight": "bold"}),
                    ],
                    style={"width": "38%", "display": "inline-block", "verticalAlign": "top"},
                ),
            ]
        ),
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    ]
)


@app.callback(
    Output("3d-view", "figure"),
    Output("ai-graph", "figure"),
    Output("alert-box", "children"),
    Input("update-interval", "n_intervals"),
)
def refresh_dashboard(_interval: int):
    traces = []
    xs: List[float] = []
    ys: List[float] = []
    zs: List[float] = []
    texts: List[str] = []
    colors: List[float] = []

    for sensor in SENSORS.values():
        latest = sensor.latest_value()
        if latest is None:
            continue

        x, y, z = sensor.pos
        xs.append(x)
        ys.append(y)
        zs.append(z)
        texts.append(f"{sensor.name}: {latest:.2f}")
        colors.append(latest)

        history = sensor.recent_values(50)
        if history:
            traces.append(
                go.Scatter3d(
                    x=[x] * len(history),
                    y=[y] * len(history),
                    z=np.linspace(z, z + 1, len(history)),
                    mode="lines",
                    line=dict(color="rgba(100,100,100,0.5)", width=2),
                    showlegend=False,
                )
            )

    traces.append(
        go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers+text",
            text=texts,
            textposition="top center",
            marker=dict(size=15, color=colors, colorscale="Viridis", showscale=True),
            name="Sensores",
        )
    )

    fig_3d = go.Figure(data=traces)
    fig_3d.update_layout(scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"), height=600)

    focus_sensor = SENSORS["Motor_Temp"]
    real_vals = focus_sensor.recent_values(30)
    fig_ai = go.Figure()
    alert_msg = ""

    if real_vals:
        fig_ai.add_trace(
            go.Scatter(
                x=list(range(len(real_vals))),
                y=real_vals,
                mode="lines+markers",
                name="Real",
            )
        )
        prediction = focus_sensor.predict_next()
        if prediction is not None:
            fig_ai.add_trace(
                go.Scatter(
                    x=[len(real_vals)],
                    y=[prediction],
                    mode="markers",
                    marker=dict(color="red", size=12, symbol="star"),
                    name="Predicción AI",
                )
            )
            if prediction > 50:
                alert_msg = f"⚠️ ALERTA: La IA predice sobrecalentamiento ({prediction:.2f}°C)."
        else:
            alert_msg = "Entrenando red neuronal... espera unos segundos."

    fig_ai.update_layout(title="Análisis Tiempo Real: Motor_Temp", height=300)
    return fig_3d, fig_ai, alert_msg


# ------------------------------ APPLICATION ----------------------------- #
def start_background_threads() -> None:
    threading.Thread(target=mqtt_worker, daemon=True).start()
    threading.Thread(target=trainer_worker, daemon=True).start()

    if SIMULATION_INTERVAL_SECONDS > 0:
        threading.Thread(target=simulator_worker, daemon=True).start()


def main() -> None:
    LOGGER.info("Gemelo Digital iniciando...")
    start_background_threads()
    app.run_server(debug=True, host=DASH_HOST, port=DASH_PORT)


if __name__ == "__main__":
    main()
