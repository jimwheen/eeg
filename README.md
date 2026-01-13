# Low-cost EEG for Alpha and Beta Wave Monitoring

## Overview
This project demonstrates a custom designed, low-cost EEG system for monitoring **alpha (8-13 Hz)** and **beta (13-30 Hz)** brain waves. It is designed for educational purposes, providing a hands-on way to learn about analog and digital filter design and study biological signal processing without the need for expensive medical equipment. 

The system implements a multi-stage analog processing pipeline feeding into a Teensy 4.0 microcontroller for real-time analysis. The accompanying software visualizes both the time-domain voltage and frequency-domain content via Fast Fourier Transform (FFT).

## Hardware Architecture
The design is based on the following signal flow block diagram:

![Signal flow block diagram](FlowChart.png)

### Simulation and Prototyping
The system was first validated using LTspice to tune component values for frequency response and stability.
> Note: The simulation below excludes the second gain stage to speed up simulation convergence.
![Full Circuit Simulation](simulation_images/full_circuit.png)

The physical prototype is currently implemented on a breadboard for modular testing.
> Note: The model also doesn't include the second gain stage.
![Breadboard Prototype](breadboard.jpg)

### Stage 1: Pre-Amplification (AD620)
The first stage uses an AD620 Instrumentation Amplifier to lift the signal out of the noise floor.
* Gain Setting: Configured for $G \approx 89.2$.
* Design Logic: This gain is high enough to capture the signal but low enough to prevent saturation from unwanted DC offsets before filtering.
* Equation:
$$G = 1 + \frac{49.4k\Omega}{R_G}$$

### Stage 2: Active Bandpass Filtering (Sallen-Key / Butterworth)
I implemented a cascaded filter design to isolate the 8-30 Hz band of interest.
* Equation:
$$f_c = \frac{1}{2\pi \cdot R \cdot C}$$
1. High-Pass Filter: Removes DC offsets and low-frequency electrode drift ($f_c \approx 7.23$ Hz).
2. Low-Pass Filter: Removes high-frequency noise and anti-aliases the signal for the ADC.
   * Design Iteration: Initially designed for $f_c \approx 32.9$ Hz. However, simulation revealed that loading effects from the subsequent Notch filter stage altered the rolloff. To compensate, I adjusted the theoretical cutoff to 72.3 Hz, which brought -3dB point closer to 30 Hz.

### Stage 3: Twin-T Notch Filter (60 Hz Rejection)
To reject power line interference (the dominant noise source) I implemented and active Twin-T Notch filter.
* Design: Based on a high-Q bootstrap design (Reference: [TI Application Note SNOA680](https://www.ti.com/lit/an/snoa680/snoa680.pdf?ts=1768248220553&ref_url=https%253A%252F%252Fwww.google.com%252F)).

However, during physical testing the bootstrapping feedback loop introduced instability and frequency drift. For the current revision, I have grounded the bootstrap node to prioritize stability over Q-factor.

### Stage 4: Instrumentation Amplifier (AD620)
A second amplification stage brings the filtered signal to appropriate voltages for the ADC. This stage matches the configuration of Stage 1 but includes a potentiometer for gain adjustment based on signal strength.

### Stage 5: DC Bias and ADC Protection
The Teensy ADC requires a 0V–3.3V input range.
* Biasing: A summing amplifier configuration shifts the AC signal to a DC offset of ~1.4V (Close to Mid-rail).
* Protection: Clamping diodes (1N4148) are installed to direct voltage spikes to the rails, protecting the microcontroller pins during transient events.

Verification of DC Bias:
![DC Offset LTspice Simulation](simulation_images/dc_off.png)

Verification of Over-Voltage Protection:
![Protection Circuit Test](simulation_images/dc_off_vspike.png)


## Software and Digital Signal Processing 
The filtered EEG signal is digitized by the Teensy 4.0 and streamed to a Python application.

* Microcontroller: Samples at 500 Hz (Nyquist = 250 Hz, well above the 30 Hz Beta target) and streams over Serial at 115200 baud.
* Python Application
  * Data Handling: Uses a rolling buffer (N=1000) for real-time analysis.
  * DSP: numpy.fft performs a Fast Fourier Transfrom to extract frequency content.
  * DC Removal: A digital high-pass filter (mean subtraction) is applied before the FFT to prevent the DC bias from affecting low frequency data.

[View the Python Code Here](EEG_test.py)


## Testing and Validation
Current testing is done with a function generator to inject known sine waves (30mV amplitude) into the signal chain. This verifies that the software FFT matches the physcial oscilloscope output.

### High-Pass Verification (3 Hz Input)
![3Hz Response](testing_images/3Hz_test.png)
Result: The signal is attenuated, confirming the High-Pass filter is correctly blocking low-frequencies below the 7 Hz cutoff.

### Passband Verification (13 Hz Input)
![13Hz Response](testing_images/13Hz_test.png)
Result: The signal passes with minimal attenuation. The FFT shows a clean spike at 13 Hz confirming functionality.

### Notch Filter Verification (60 Hz Input)
![60Hz Response](testing_images/60Hz_test.png)
Result: The 60 Hz input is significantly attenuated, validating the Twin-T notch filter's rejection of power line noise.

## Component Choices & Safety Considerations
* TL072 Op-Amps: Selected for JFET inputs (ultra-high input impedance) to minimize current draw from electrode signals.
* Isolation: The system is strictly battery-powered (+9V and -9V) to ensure complete electrical isolation.
* Computer Safety: When connected to a PC an electrically isolated USB hub is required.
* Future Safety: A Driven-Right-Leg (DRL) circuit and additional input protection clamps are planned for the final prototype.

## Future Roadmap
* PCB Design: Convert the breadboard prototype to a PCB.
* Electrode Integration: Begin testing with electrodes and human subjects.
* Digital Filtering: Implement additional filters using Python for further noise reduction.
