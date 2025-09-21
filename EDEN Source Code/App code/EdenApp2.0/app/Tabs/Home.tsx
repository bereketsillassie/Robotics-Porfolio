import 'react-native-gesture-handler';
import React, { useState } from 'react';
import { View, StyleSheet, Alert, Text, TouchableOpacity, Modal, TextInput, Pressable } from "react-native";
import { Calendar } from "react-native-calendars";
import { format } from 'date-fns';
import { useContext } from 'react';
import { PlantingContext } from "../Tabs/PlantingContext";



export default function EdCalendar() {

  

  const npkDatabase = {
    // Flowers
    Tulip: { n: 100, p: 200, k: 200 },
    Rose: { n: 150, p: 150, k: 150 },
    Lavender: { n: 80, p: 40, k: 80 },
    Sunflower: { n: 80, p: 60, k: 100 },
    Daisy: { n: 70, p: 50, k: 70 },
  
    // Herbs
    Mint: { n: 120, p: 60, k: 90 },
    Basil: { n: 120, p: 60, k: 90 },
    Cilantro: { n: 100, p: 60, k: 80 },
    Oregano: { n: 100, p: 60, k: 80 },
    Parsley: { n: 110, p: 60, k: 90 },
    Thyme: { n: 80, p: 40, k: 80 },
  
    // Vegetables
    Tomato: { n: 120, p: 50, k: 180 },
    Cucumber: { n: 100, p: 60, k: 120 },
    Lettuce: { n: 150, p: 50, k: 200 },
    Carrot: { n: 100, p: 70, k: 150 },
    Broccoli: { n: 140, p: 80, k: 180 },
    BellPepper: { n: 120, p: 60, k: 160 },
    Spinach: { n: 150, p: 60, k: 150 },
    Corn: { n: 150, p: 60, k: 200 },
  
    // Fruits
    Strawberry: { n: 100, p: 40, k: 120 },
    Blueberry: { n: 80, p: 40, k: 100 },
    Apple: { n: 150, p: 30, k: 200 },
    Lemon: { n: 140, p: 60, k: 150 },
    Watermelon: { n: 100, p: 40, k: 120 },
  
    // Trees
    Tree: { n: 500, p: 200, k: 300 }, // generic
    Oak: { n: 400, p: 150, k: 200 },
    Maple: { n: 350, p: 150, k: 250 },
    Pine: { n: 300, p: 100, k: 150 },
    Palm: { n: 450, p: 200, k: 300 }
  };
  
  
  const plantingContext = useContext(PlantingContext);
  const plantingData = plantingContext?.plantingData || {};
  const setPlantingData = plantingContext?.setPlantingData || (() => {});
  const [selectedDateInfo, setSelectedDateInfo] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [newPlantName, setNewPlantName] = useState("");
  const [newPodNumber, setNewPodNumber] = useState("");
  const [newPlantDate, setNewPlantDate] = useState("");
  

  const plantData = {
    '2025-04-01': { plantName: "tulip", podNumber: 55 },
    '2025-04-05': { plantName: 26, podNumber: 50 },
    '2025-04-10': { plantName: 19, podNumber: 60 },
    '2025-04-15': { plantName: 21, podNumber: 53 },
  };

  const handleAddPlant = () => {
    Alert.prompt("Plant Name", "Enter the name of the plant:", [
      {
        text: "Cancel",
        style: "cancel",
      },
      {
        text: "Next",
        onPress: (plantName) => {
          if (!plantName) return;
  
          Alert.prompt("Pod Number", "Which pod is this plant in?", [
            {
              text: "Cancel",
              style: "cancel",
            },
            {
              text: "Next",
              onPress: (podNumber) => {
                if (!podNumber) return;
  
                Alert.prompt("Planting Date (YYYY-MM-DD)", "What day was it planted?", [
                  {
                    text: "Cancel",
                    style: "cancel",
                  },
                  {
                    text: "Add",
                    onPress: (plantDate) => {
                      if (!plantDate) return;
  
                      setlantingData(prev => ({
                        ...prev,
                        [plantDate]: [{
                          plantName,
                          podNumber
                        }]
                      }));
                    }
                  }
                ]);
              }
            }
          ]);
        }
      }
    ]);
  };
  

  // THis create markedDates object to highlight dates with sensor data
  const markedDates = Object.keys(plantingData || {}).reduce((acc, date) => {
    
    acc[date] = {
      marked: true,
      dotColor: '#17ae73', 
      selected: false,
      
    };
    return acc;
  }, {});

  // Handle day press to display sensor data
  const onDayPress = (day) => {
    const date = day.dateString;
    const localDate = new Date(date + 'T00:00:00');
    const formattedDate = format(localDate, 'MMMM dd, yyyy');
  
    const data = plantingData[date];
  
    if (data && Array.isArray(data)) {
      setSelectedDateInfo({
        date: formattedDate,
        plants: data
      });
    } else {
      setSelectedDateInfo(null);
      Alert.alert("No plant data", `Nothing planted on ${formattedDate}`);
    }
  };

    return (

      <View style={styles.container}>
        {/* Static Text: Heading or Description */}

        <Calendar
          // Initially visible month.
          current={'2025-04-01'}
          // Minimum date that can be selected
          minDate={'2025-01-01'}
          // Maximum date that can be selected
          maxDate={'2025-12-31'}
          // Handler which gets executed on day press
          onDayPress={onDayPress}
          monthFormat={'MMMM yyyy'}
          // Enable horizontal scrolling
          horizontal={true}
          // Specify style for calendar container
          markedDates={markedDates}
          // Mark Calendar
          style={styles.calendar}
          theme={{
            backgroundColor: '#f5f3eb',
            calendarBackground: '#f5f3eb', 
            textSectionTitleColor: '#2e5339', 
            selectedDayBackgroundColor: '#6c9a8b',    
            selectedDayTextColor: '#ffffff',
            todayTextColor: '#2e5339',
            dayTextColor: '#2e5339',
            textDisabledColor: '#c9b79c',
            dotColor: '#6c9a8b',
            selectedDotColor: '#ffffff',
            arrowColor: '#6c9a8b',
            monthTextColor: '#2e5339',
            indicatorColor: '#6c9a8b',
            textDayFontWeight: '400',
            textMonthFontWeight: 'bold',
            textDayHeaderFontWeight: '600',
            textDayFontSize: 16,
            textMonthFontSize: 18,
            textDayHeaderFontSize: 14
          }}
        />

        <View style={styles.container2}>
          <Text style={styles.textAboveCalendar}>Select a Date to View Sensor Data</Text>

          {/* Dynamic Text: Information about the selected date */}
          {selectedDateInfo && (
            <View style={styles.infoContainer}>
              <Text style={styles.selectedDateText}>Planted Date: {selectedDateInfo.date}</Text>

              {selectedDateInfo.plants.map((plant, index) => (
                <View key={index}>
                  <Text style={styles.temperatureText}>🌱 Plant: {plant.plantName}</Text>
                  <Text style={styles.humidityText}>🪴 Pod: {plant.podNumber}</Text>
                  {plant.npk && (
                    <>
                      <Text style={styles.humidityText}>🌾 Expected NPK Ratio - N: {plant.npk.n}, P: {plant.npk.p}, K: {plant.npk.k}</Text>
                    </>
                  )}
                  
                  <Text style={styles.humidityText}>—</Text>
                </View>
              ))}
            </View>
          )}
        </View>

        <TouchableOpacity
          style={styles.floatingButton}
          onPress={() => setModalVisible(true)}
        >
          <Text style={styles.floatingButtonText}>+</Text>
        </TouchableOpacity>

        <Modal
          animationType="slide"
          transparent={true}
          visible={modalVisible}
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalView}>
              <Text style={styles.modalTitle}>Add New Plant</Text>

              <TextInput
                style={styles.modalInput}
                placeholder="Plant Name"
                value={newPlantName}
                onChangeText={setNewPlantName}
              />
              <TextInput
                style={styles.modalInput}
                placeholder="Pod Number"
                keyboardType="numeric"
                value={newPodNumber}
                onChangeText={setNewPodNumber}
              />
              <TextInput
                style={styles.modalInput}
                placeholder="Date (YYYY-MM-DD)"
                value={newPlantDate}
                onChangeText={setNewPlantDate}
              />

              <View style={styles.modalButtons}>
                <Pressable onPress={() => setModalVisible(false)}>
                  <Text style={styles.cancelButton}>Cancel</Text>
                </Pressable>
                <Pressable onPress={() => {
                  if (newPlantName && newPodNumber && newPlantDate) {
                    setPlantingData(prev => {
                      const updated = { ...prev };
                      if (!updated[newPlantDate]) {
                        updated[newPlantDate] = [];
                      }
                      updated[newPlantDate].push({
                        plantName: newPlantName,
                        podNumber: newPodNumber,
                        npk: npkDatabase[newPlantName] || null,
                      });
                      return updated;
                    });

                    setModalVisible(false);
                    setNewPlantName("");
                    setNewPodNumber("");
                    setNewPlantDate("");
                  }
                }}>
                  <Text style={styles.addButton}>Add</Text>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>
      </View>
    
    );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#e4dfc9',
  },
  container2: {
    flex: 1,
    alignItems: 'center',
    
  },
  textAboveCalendar: {
    fontSize: 16,
    color: '#2e5339',
    marginBottom: 10,
    marginTop: 20,
    textAlign: 'center',
  },
  calendar: {
    width: '100%',
    backgroundColor: '#f5f3eb',
  },
  infoContainer: {
    marginTop: 15,
    marginBottom: 20,
    padding: 10,
    width: '90%',
    borderRadius: 10,
    backgroundColor: '#fffaf3',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  selectedDateText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2e5339',
  },
  
  temperatureText: {
    color: '#6c9a8b',
    fontSize: 16,
  },
  humidityText: {
    color: '#6c9a8b',
    fontSize: 16,
  },
  noDataText: {
    marginTop: 20,
    fontSize: 16,
    color: '#a68b6d',
    fontStyle: 'italic',
  },
  screenContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  screenText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2e5339',
  },
  floatingButton: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: '#6c9a8b',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  floatingButtonText: {
    fontSize: 24,
    color: 'white',
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  modalView: {
    backgroundColor: "#fffaf3",
    borderRadius: 10,
    padding: 20,
    width: "85%",
    elevation: 5,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
    textAlign: "center",
    color: '#2e5339',
  },
  modalInput: {
    borderWidth: 1,
    borderColor: "#c9b79c",
    padding: 10,
    marginVertical: 6,
    borderRadius: 5,
    backgroundColor: "#ffffff",
  },
  modalButtons: {
    marginTop: 10,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  cancelButton: {
    color: "#a68b6d",
    padding: 10,
  },
  addButton: {
    color: "#6c9a8b",
    fontWeight: "bold",
    padding: 10,
  },
});


