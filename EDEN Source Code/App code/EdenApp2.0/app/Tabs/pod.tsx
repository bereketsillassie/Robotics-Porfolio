import { StyleSheet, Text, View } from "react-native";
import { useEffect, useState } from "react";


type SensorData = {
  temperature: number;
  humidity: number;
  moisture: number;
  light: number;
};

function Pod() {

  
  const [pod1Data, setPod1Data] = useState<SensorData | null>(null);
  const [pod2Data, setPod2Data] = useState<SensorData | null>(null);
  const [pod3Data, setPod3Data] = useState<SensorData | null>(null);
  const [pod4Data, setPod4Data] = useState<SensorData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      

      try {
        const response = await fetch("http://192.168.1.126:5000/get-pod-data", {
          headers: {
            "X-API-Key": "mysecretkey123"
          }
        });
      
        if (!response.ok) {
          console.warn(`Response error: ${response.status}`);
        }
      
        const json = await response.json();
        
      
        setPod1Data(json.pod1);
        setPod2Data(json.pod2);
        setPod3Data(json.pod3);
        setPod4Data(json.pod4);
      } catch (error) {
        console.error("Failed to fetch data from Flask:", error);
      }
  

    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenText}>Sensor Information</Text>
      <View style={styles.podContainer}>
        <Text style={styles.podtitleText}>Plant Pod 1</Text>
        <Text style={styles.sensordataText}>Light: {pod1Data ? `${pod1Data.light} lux` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Temperature: {pod1Data ? `${pod1Data.temperature}°F` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Humidity: {pod1Data ? `${pod1Data.humidity}%` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Moisture: {pod1Data ? `${pod1Data.moisture}%` : "Loading..."}</Text>
      </View>
      <View style={styles.podContainer}>
        <Text style={styles.podtitleText}>Plant Pod 2</Text>
        <Text style={styles.sensordataText}>Light: {pod2Data ? `${pod2Data.light} lux` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Temperature: {pod2Data ? `${pod2Data.temperature}°F` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Humidity: {pod2Data ? `${pod2Data.humidity}%` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Moisture: {pod2Data ? `${pod2Data.moisture}%` : "Loading..."}</Text>
      </View>
      <View style={styles.podContainer}>
        <Text style={styles.podtitleText}>Plant Pod 3</Text>
        <Text style={styles.sensordataText}>Light: {pod3Data ? `${pod3Data.light} lux` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Temperature: {pod3Data ? `${pod3Data.temperature}°F` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Humidity: {pod3Data ? `${pod3Data.humidity}%` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Moisture: {pod3Data ? `${pod3Data.moisture}%` : "Loading..."}</Text>
      </View>
      <View style={styles.podContainer}>
        <Text style={styles.podtitleText}>Plant Pod 4</Text>
        <Text style={styles.sensordataText}>Light: {pod4Data ? `${pod4Data.light} lux` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Temperature: {pod4Data ? `${pod4Data.temperature}°F` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Humidity: {pod4Data ? `${pod4Data.humidity}%` : "Loading..."}</Text>
        <Text style={styles.sensordataText}>Moisture: {pod4Data ? `${pod4Data.moisture}%` : "Loading..."}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e4dfc9',
  },
  screenText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  podContainer: {
    marginTop: 7,
    marginBottom: 7,
    padding: 10,
    borderRadius: 10,
    width: '90%',
    height: 'auto',
    backgroundColor: '#fffaf3',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,

  },
  sensordataText: {
    color: '#6c9a8b',
    fontSize: 18,
    textAlign: 'center',

  },
  podtitleText: {
    color: '#2e5339',
    fontSize: 25,
    fontWeight: 'bold',
    textAlign: 'center',
  }

});

export default Pod;