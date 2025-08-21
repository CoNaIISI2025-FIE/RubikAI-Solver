# 🧠 IA para Resolver Variantes del Cubo de Rubik

Este proyecto implementa una inteligencia artificial basada en **deep learning** y **heurísticas** para resolver diferentes variantes del cubo de Rubik: 3x3, 4x4, 5x5, Megaminx y Pyraminx. Desarrollado como parte de un trabajo práctico para la Facultad de Ingeniería del Ejército (UNDEF).

## 🚀 Tecnologías Utilizadas

- Python 3.x  
- TensorFlow / PyTorch  
- NumPy  
- OpenCV (opcional para visualización)  

## 🎯 Objetivo

Crear un sistema capaz de resolver automáticamente cubos de Rubik utilizando redes neuronales profundas entrenadas con simulaciones y optimizadas con reglas heurísticas. El enfoque permite adaptarse fácilmente a distintas estructuras sin programar manualmente cada tipo.

## 📁 Estructura del Proyecto

- `/models`: Arquitecturas y modelos entrenados  
- `/data`: Scripts para generar datasets  
- `/solver`: Lógica de resolución  
- `/notebooks`: Pruebas y análisis exploratorios  
- `main.py`: Script principal para ejecutar el sistema  

## 🧪 Cómo Ejecutarlo

```bash
git clone https://github.com/AgustinGimenezFIE/IACuboRubik.git
cd rubik-ia-solver
pip install -r requirements.txt
python main.py
