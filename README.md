# Low-cost EEG for Alpha and Beta Wave Monitoring

## Overview
This project demonstrates a custom designed, low-cost EEG system for monitoring **alpha (8-13 Hz)** and **beta (13-30 Hz)** brain waves. It is designed for educational purposes, providing a hands-on way to learn about **analog and digital filter design** and study biological signal processing without the need for expensive medical equipment. 

The system implements a multi-stage analog processing pipeline feeding into a Teensy 4.0 microcontroller for real-time analysis. The accompanying software visualizes both the time-domain voltage and frequency-domain content via Fast Fourier Transform (FFT).

## Hardware Architecture (Ongoing)
The design is based on the following signal flow block diagram:

![Signal flow block diagram](FlowChart.png)

### Simulation and Prototyping
The system was first validated using LTspice to tune component values for frequency response and stability.
> Note: The simulation below excludes the second gain stage to optimize simulation convergence speed.
![Full Circuit Simulation](simulation_images/full_circuit.png)

The physical prototype is currently implemented on a breadboard for modular testing.
> Note: Also doesn't include the second gain stage
![Breadboard Prototype](breadboard.jpg)

### Stage 1: Instrumentation Amplifier (AD620)
Assuming microvolt level signals (~0.5 to 200 microvolts) the AD620 was configured for a gain of 89.2 to not overamplify the unwanted noise but to bring the signals within appropriate range for analog filtering.

Using the equation Gain = 1 + 49400/Rg = 1 + 49400/560ohm = 89.2.

### Stage 2: Bandpass Filtering (Butterworth/Sallen-Key):
Implemented bandpass filtering using first a highpass then a low pass second order butterworth filter. The cutoff frequnecy for the low pass was designed to be ~7.23Hz (fc = 1/(2pi*100k*220nF)). The lowpass was initially designed for cutoff of ~32.9Hz (fc = 1/(2pi*100k*220nF)).

However, after applying the notch filter in simulation the rolloff significantly increased for the lowpass so the cutoff was shifted significantly higher to get closer to the -3dB point. With theoretical of ~72.3Hz (fc = 1/(2pi*22k*100nF)).

This ensured that the desired frequency content would remain for analysis.

### Stage 3: Twin-T Notch Filter (60 Hz Rejection)
Since the human body acts like an antenna to decrease power line interference a notch filter was added. The filter follows a bootstrap design to increase the Q factor and have a sharper notch. The design was based off an adjustable [High Q Notch Filter](https://www.ti.com/lit/an/snoa680/snoa680.pdf?ts=1768248220553&ref_url=https%253A%252F%252Fwww.google.com%252F) design. 

In practice however this circuit was giving me problems leading to a shifted notch and reduced Q so I've temporily grounded the bootstrap and will see if its needed when testing later.

### Stage 4: Instrumentation Amplifier (AD620)
After analog filtering the signal is amplied for a second time for analyis on the computer. Currently the second amplification circuit will be the same as in stage 1 with a potnetitiomter to adjust the gain in order to set the signal at the appropraite scale for analysis.

### Stage 5: Summing Amp. (Bias)
The output wave is shifted to ensure the correct voltage range is input into the teensy (0V-3.3V)using the voltage divided 3.3V output from the teensy and decoupling capacitor???. The DC offset is ~1.3V close to center for whats accepted by the input pins on the teensy (Vout = [1+Ra/Rb](v1+V2/2). The diodes ensure protection of the teensy input pin from overvoltage events.

Circuit Tested with expected max output:
![DC Offset](simulation_images/dc_off.png)

Circuit Tested in the case of an overvoltage veent:
![DC Offset Overvoltage](simulation_images/dc_off_vspike.png)


## Software and Digital Signal Processing (Ongoing)
The filtered EEG signal is read by one of the adc pins on the teensy. The baud rate is set for 115200 baud to ensure fast enough serial communication. The sample rate is also set for 500hz with a nyquist frequency of 250hz well above the 30Hz beta wave target to avoid aliasing and getting clean output. 

The software is written in python and uses the numpy library to apply the FFT to the input signal. Both the input voltage waveform and frequency spectrum is plotted. The buffer size is set to 1000 for close to real time analysis. The signals dc offset is also removed for the fourier analysis my subtracting the mean voltage (essentially applying a high pass filter at 0hz) to ensure the dc offset doesnt overpower the frequency content.

The code can be viewed here. [EEG_test.py](EEG_test.py)


## Testing (Progress)
The circuit is currently being tested using a fixed sine wave input from a signal generator at various frequencies to observe the chnages in the frequency repsone and compare teh software resulst with teh oscillsiocpe output. The input is 30mV so only one of the ad620 amplification circuits is being used.

Some tests at various different frequencies are shown below:

### 3Hz Test
![3Hz Response](testing_images/3Hz_test.png)
The software result matches that of the output oscillscope waveform aswell as the input sine wave frequency as seen by the FFT spike. The signal strength is attenuated as expected by the highpass filtering.

### 13Hz Test
![13Hz Response](testing_images/13Hz_test.png)
The software result matches that of the output oscillscope waveform aswell as the input sine wave frequency as seen by the FFT spike. The signal strength is minimally attenuated as expected.

### 60Hz Test
![60Hz Response](testing_images/60Hz_test.png)
The software result matches that of the output oscillscope waveform aswell as the input sine wave frequency as seen by the FFT spike. The signal strength is strongly attenuated by the notch filter.

## Component Choices / Safety Considerations
The TL072 chip was chosen for its high input impedance keeping the signal clean for processing. The +9V and -9V rails are battery powered for safety when using the system on humans and the computer must be disconnected from the wall with an electrically isolated usb input port. Often a driven-right-leg circuit is used for cancelling out noise aswell. This may be added in the future if noise is overwhelming, but I wanted to focus on other filtering techniques first then add if needed. When the electrodes are also integrated I will add a further protection circuit to further protetc in an overvoltage event.

## Future Work
A portection circuit will be simulated and added. Then testing will begin with electrodes. Digital filters may also be added to clean up the true signal. Once a viable product is complete the circuit will be converted to a pcb so it is modular and robust and opensource for others to experment with.
