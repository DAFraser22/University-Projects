#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MAX_TIMINGS 85         // Max number of data to read from the DHT11 sensor
#define DHT_PIN 7              // Connects to the DHT11 data line
#define BUTTON_PIN 0           // Pin connects to the button

int sensor_data[5] = { 0, 0, 0, 0, 0 };  // Buffer to store DHT11 data
float highest_temperature = -100.0;
int  is_first_write = 1;

// Function reads temperature and humidity info from the DHT11 sensor
void write_sensor_data_to_file(int humidity_int, int humidity_dec, int temp_int, int temp_dec, float highest_temp) {

	FILE *file;
	
	if (is_first_write == 1) {
		file  = fopen("sensor_output.txt", "w"); // open file in append mode
		is_first_write = 0;
	} else {
		file  = fopen("sensor_output.txt", "a"); // open file in append mode for subsequent entries
	}

	if (file == NULL) {
		printf("Error opening file!\n");
		return;
	}
	// Write data to file
	fprintf(file, "Humidity = %d.%d %% Temperature = %d.%d °C\n", humidity_int, humidity_dec, temp_int, temp_dec);
	fclose(file); // closes file
}

void read_sensor_data() {

    uint8_t previous_state = HIGH;      // Previous state of the DHT pin
    uint8_t pulse_counter = 0;          // Duration of each pulse
    uint8_t bit_index = 0, i;           // Bit and loop counters
    float fahrenheit_temperature;       // Fahrenheit variable
    float current_temperature;          // Current temperature in Celsius

    // Clear sensor data buffer

    for (i = 0; i < 5; i++) {

        sensor_data[i] = 0;

    }

    // Signal the DHT11 sensor to start
    pinMode(DHT_PIN, OUTPUT);
    digitalWrite(DHT_PIN, LOW);

    // Keeps signal low for 18ms
    delay(18);
    digitalWrite(DHT_PIN, HIGH);

    // Signal is high for 40µs
    sensor_data[0], 
    delayMicroseconds(40);        
    pinMode(DHT_PIN, INPUT);

    // Read the DHT11 data

    for (i = 0; i < MAX_TIMINGS; i++) {

        pulse_counter = 0;

        // Measures how long the signal stays in the same state
        while (digitalRead(DHT_PIN) == previous_state) {

            pulse_counter++;
            delayMicroseconds(1);

            if (pulse_counter == 255) {
                break;
            }

        }

        previous_state = digitalRead(DHT_PIN);

        if (pulse_counter == 255) {
            break;
        }

        // Skip the first few transitions, then start recording data bits
        if ((i >= 4) && (i % 2 == 0)) {
            sensor_data[bit_index / 8] <<= 1;  // Shift the byte to the left

            if (pulse_counter > 16) {         // A long pulse represents a 1
                sensor_data[bit_index / 8] |= 1;
            }

            bit_index++;
        }
    }

    // Verify the checksum and display the data
    if ((bit_index >= 40) &&

        (sensor_data[4] == ((sensor_data[0] + sensor_data[1] + sensor_data[2] + sensor_data[3]) & 0xFF))) {
        current_temperature = sensor_data[2] + sensor_data[3] / 10.0; // Combine integer and decimal parts for the temperature
        fahrenheit_temperature = current_temperature * 9. / 5. + 32;  // Calculte Fahrenheit temperature from Celsius 

        // Check if the current temperature is higher than the current highest
        if (current_temperature > highest_temperature) {
            highest_temperature = current_temperature; // Update the highest temperature
        }

        // Print Readings
        printf("Humidity = %d.%d %% Temperature = %d.%d °C (%.1f °F)\n", sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3], fahrenheit_temperature);
	
	// call write to file function
	write_sensor_data_to_file(sensor_data[0], sensor_data[1], sensor_data[2],sensor_data[3],highest_temperature);  

    } else {
        printf("Failed to read data from sensor, trying again.\n");
    }

}

int main() {

    printf("DHT11 Temperature & Humidity Sensor Program\n");
    printf("Press the button to take 20 readings from the sensor.\n");

    // Initialize wiringPi library
    if (wiringPiSetup() == -1) {
        exit(1);
    }

    // Configure the button GPIO pin
    pinMode(BUTTON_PIN, INPUT);
    pullUpDnControl(BUTTON_PIN, PUD_DOWN);  // Enable pull-down resistor

    while (1) {
        // Check if the button is pressed
        if (digitalRead(BUTTON_PIN) == HIGH) {

            printf("Button pressed! Starting 20 readings...\n");

            for (int reading_count = 0; reading_count < 20; reading_count++) {
                read_sensor_data();
                delay(1000);
            }

            printf("Completed 20 readings.\n");
			printf("Highest Temperature Recorded: %.1f °C\n", highest_temperature);
            printf("Sending file to aws\n");
			
			// Calls the Python Script
			system("python3 pythonBucket.py /home/pi/sensor_output.txt");
            printf("Press the button again to take more readings.\n");
        }
    }
    return 0;
}
