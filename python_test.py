import serial
import matplotlib.pyplot as plt
import numpy as np

# Connect to Teensy 
ser = serial.Serial('COM3', 115200) 

# Sampling rate (matches Teensy delay of 2ms)
FS = 500 

# Number of samples kept in memory
BUFFER_SIZE = 1000 

# Initialzes buffer with midpoint voltage (3.3V/2 = 1.65V) - prevents weird startup FFT spikes
data_history = [1.65] * BUFFER_SIZE

# Setup the Graphs (interactive plot)
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.4)

# Top Plot: Time Domain
line_time, = ax1.plot(data_history)
ax1.set_ylim(0, 3.3)
ax1.set_title("Time Domain: EEG Signal")
ax1.set_ylabel("Voltage (V)")

# Bottom Plot: Frequency Domain (FFT)

# Only positive frequencies(rfft) - determines frequency values for fft bins
frequencies = np.fft.rfftfreq(BUFFER_SIZE, 1/FS)
line_fft, = ax2.plot(frequencies, np.zeros(len(frequencies)))
ax2.set_xlim(0, 100)  # Standard EEG range (0-100Hz)
ax2.set_ylim(0, 0.5)  # Amplitude
ax2.set_title("Frequency Domain: FFT")

# Adds a number every 5Hz (0, 5, 10, 15...)
ax2.set_xticks(np.arange(0, 101, 5)) 

ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
ax2.set_ylabel("Amplitude")
ax2.set_xlabel("Frequency (Hz)")

# Continously reads serial and updates plots
while True:
    if ser.in_waiting > 0:
        try:
            raw_data = ser.readline().decode().strip()
            if not raw_data: continue
            
            # Converts ADC value to voltage (Teensy ADC gives values 0-1023)
            voltage = (float(raw_data) / 1023.0) * 3.3

            # Adds newest sample and removes oldest (constant buffer length)
            data_history.append(voltage)
            data_history.pop(0)
            
            if ser.in_waiting < 10:
                # Update Time Plot
                line_time.set_ydata(data_history)
                
                # Calculate FFT
                # Remove the DC offset (mean) so the 0Hz spike doesn't ruin the scale (like highpass at 0hz)
                signal = np.array(data_history) - np.mean(data_history)
                fft_mag = np.abs(np.fft.rfft(signal)) / BUFFER_SIZE
                
                # Update FFT Plot
                line_fft.set_ydata(fft_mag)
                
                # Forces redraw of updated data
                fig.canvas.draw()
                fig.canvas.flush_events()
            
        except Exception as e:
            continue