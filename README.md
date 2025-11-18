![Tiktokenizer](https://user-images.githubusercontent.com/1443449/222597674-287aefdc-f0e1-491b-9bf9-16431b1b8054.svg)

***

# Tiktokenizer

Online playground for `openai/tiktoken`, calculating the correct number of tokens for a given prompt.

Special thanks to [Diagram](https://diagram.com/) for sponsorship and guidance.

https://user-images.githubusercontent.com/1443449/222598119-0a5a536e-6785-44ad-ba28-e26e04f15163.mp4

## Acknowledgments

- [T3 Stack](https://create.t3.gg/)
- [shadcn/ui](https://github.com/shadcn/ui)
- [openai/tiktoken](https://github.com/openai/tiktoken)

## Gemelo Digital (MQTT + LSTM)

Este repositorio ahora incluye `gemelo_legendario.py`, un script independiente que escucha sensores reales vía MQTT, entrena modelos LSTM ligeros y muestra la planta en 3D con Dash.

### Dependencias

```bash
python -m venv .venv && source .venv/bin/activate
pip install dash plotly numpy paho-mqtt scikit-learn tensorflow
```

### Ejecución

```bash
python gemelo_legendario.py
```

El dashboard se expone por defecto en `http://localhost:8055`. Personaliza la conexión y el entrenamiento con variables de entorno:

- `GEMELO_MQTT_BROKER`, `GEMELO_MQTT_PORT`, `GEMELO_MQTT_TOPIC`
- `GEMELO_LOOK_BACK`, `GEMELO_BUFFER_SIZE`, `GEMELO_TRAIN_INTERVAL`
- `GEMELO_SIM_INTERVAL` (pon `0` para desactivar el simulador interno)
- `GEMELO_DASH_HOST`, `GEMELO_DASH_PORT`

Si dispones de un ESP32 con MicroPython, publica lecturas en `test.mosquitto.org` bajo `jaime/planta/#` (ejemplo en las instrucciones del proyecto) y el gemelo las incorporará automáticamente. Sin hardware, el simulador integrado mantiene vivo el flujo de datos para pruebas locales.
