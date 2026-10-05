# Artificial Intelligence & Perception

The perception system of the Writer Robot combines hardware sensors (Thermal, Gas) with computer vision to confidently detect victims and hazards.

## Vision Model

*   **Architecture**: YOLOv8n (Nano)
*   **Optimization**: INT8 Quantization to run efficiently on the Raspberry Pi 4 CPU without specialized hardware accelerators.
*   **Classes**: `person`
*   **Dataset**: 5438 images from the Roboflow COCO person subset, fine-tuned for rescue scenarios.

## Performance Metrics

Evaluation on the validation set (Epoch 236):
*   **mAP50**: 72.16%
*   **Precision**: 84%
*   **Recall**: 62%
*   **F1 Score**: 0.71 at confidence threshold 0.340
*   **True Positive Rate (Person)**: 93%

*Evidence of these metrics can be found in `runs/detect/writer_robot_vision_v3-4/results.csv` and the generated plots (`BoxF1_curve.png`, `confusion_matrix_normalized.png`).*

## Sensor Fusion

Vision alone is insufficient in dense smoke or debris. The Writer Robot requires cross-validation from the MLX90640 Thermal array and MQ gas sensors before marking a high-confidence positive detection and dropping a beacon.
