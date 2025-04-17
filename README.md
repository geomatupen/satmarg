
# Satellite Overpass Prediction and Orbit Calculation

This project helps predict satellite overpasses based on user inputs like date range and location. It also provides actual image capture times for different satellites. The project consists of two main components:

1. **SatMarg (Orbit Calculation)**: This Jupyter notebook calculates the orbit of satellites using the LTE (Low Earth Orbit) method.
2. **ImageCapture (Image Capture Times)**: This file contains information about when images were captured by different satellites.

## Features

- **Satellite Orbit Prediction**: Given a location and date range, you can predict when satellites will be passing over that area.
- **Actual Image Capture Times**: Provides the actual times when different satellites captured images over a specific location.
  
## Requirements

- Python 3.x
- Jupyter Notebook (for running SatMarg)
- Required libraries (e.g., `numpy`, `pandas`, `matplotlib`, etc.)

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
```

## Usage

1. **SatMarg (Orbit Calculation)**:
   - Open the `SatMarg` Jupyter notebook.
   - Input your desired location (latitude and longitude) and date range.
   - The notebook will calculate the predicted satellite orbits and their overpass times.

2. **ImageCapture (Image Capture Times)**:
   - Open the `ImageCapture` file.
   - It provides actual satellite image capture times for various satellites.

## Example

To calculate a satellite's overpass prediction for a specific location and date range:

```python
# Example in SatMarg
location = (47.81306, 13.04667)  # Latitude, Longitude
start_datetime = "2025-02-01T00:00:00Z"
end_datetime = "2025-06-13T23:59:59Z"

# Call your function to calculate overpasses here
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
