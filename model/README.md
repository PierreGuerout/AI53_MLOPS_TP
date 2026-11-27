# Supplied model

The API loads the bundled ONNX model at startup and runs it on the CPU. Check the version returned by the API against the expected version below.

| Field | Value |
| --- | --- |
| Model file | `bean-cnn.onnx` |
| Expected model version | `phase1-reference-v1` |
| Class labels in model order | `angular_leaf_spot`, `bean_rust`, `healthy` |
| Model input | One RGB image resized to 96 × 96 pixels |
