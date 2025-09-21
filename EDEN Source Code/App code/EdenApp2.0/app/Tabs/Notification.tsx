import { StyleSheet, View, Text, FlatList, Button, TouchableOpacity, Alert } from "react-native";
import { useEffect, useState, useContext } from "react";
import { PlantingContext } from "../Tabs/PlantingContext";


function Notification() {
  const [notifications, setNotifications] = useState([]);
  const plantingContext = useContext(PlantingContext);
  const plantingData = plantingContext?.plantingData || {};

  const fetchNotifications = async () => {
    try {
      // Pi is : 192.168.1.126
      const res = await fetch("http://192.168.1.126:5000/notifications", {
        headers: {
          "X-API-Key": "mysecretkey123"
        }
      });
      const data = await res.json();
      setNotifications(data);
    } catch (error) {
      console.error("Failed to Fetch the notifications:", error);
    }
  };

  const clearAll = async () => {
    await fetch("http://192.168.1.126:5000/notifications", { 
      method: "DELETE",
      headers: {
        "X-API-Key": "mysecretkey123"
      }
    });
    setNotifications([]); // instantly update UI
  };

  const deleteOne = async (index) => {
    const actualIndex = notifications.length - 1 - index; // reverse mapping
    await fetch(`http://192.168.1.126:5000/notifications/${actualIndex}`, { 
      method: "DELETE",
      headers: {
        "X-API-Key": "mysecretkey123"
      }
    });
    fetchNotifications(); // refresh after deletion
  };

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
  

  const [selectedNotification, setSelectedNotification] = useState(null);
  const [dropdownVisible, setDropdownVisible] = useState(false);

  // When user taps notification:
  const handleNotificationTap = (notification) => {
    setSelectedNotification(notification);
    setDropdownVisible(true);
  };

  // After pod is selected:
  const handlePodSelection = (podNumber) => {
    let foundPlant = null;
    const allDates = Object.keys(plantingData).sort((a, b) => new Date(b) - new Date(a));
  
    // Search plantingData
    for (const date of allDates) {
      const plants = plantingData[date];
      if (Array.isArray(plants)) {
        const match = plants.find(p => Number(p.podNumber) === Number(podNumber));
        if (match) {
          foundPlant = match;
          break;
        }
      }
    }
  
    if (foundPlant) {
      const plantName = foundPlant.plantName;
      const expectedNPK = npkDatabase[plantName];
  
      if (expectedNPK) {

        const measuredN = selectedNotification?.npk?.n ?? null;
        const measuredP = selectedNotification?.npk?.p ?? null;
        const measuredK = selectedNotification?.npk?.k ?? null;

        if (measuredN !== null && measuredP !== null && measuredK !== null) {
          let recommendation = "";
    
          if (measuredN < expectedNPK.n) recommendation += "Add Nitrogen (N)\n";
          if (measuredP < expectedNPK.p) recommendation += "Add Phosphorus (P)\n";
          if (measuredK < expectedNPK.k) recommendation += "Add Potassium (K)\n";
    
          if (recommendation === "") {
            recommendation = "✅ NPK levels are good! No action needed.";
          }

          Alert.alert(
            `🌱 Plant: ${plantName}`,
            `Recommended NPK:\nN: ${expectedNPK.n}, P: ${expectedNPK.p}, K: ${expectedNPK.k}\n\nMeasured NPK:\nN: ${measuredN}, P: ${measuredP}, K: ${measuredK}\n\n${recommendation}`
          );
        } else {
          Alert.alert("No Real Data", "Real NPK readings were not found for this notification.");
        }
        
      } else {
        Alert.alert("No NPK Data", `No expected NPK values found for ${plantName}.`);
      }
    } else {
      Alert.alert("No Plant Found", `No plant is logged in Pod ${podNumber}. Please enter planting data on the Home Page.`);
    }
  
    setDropdownVisible(false);
  };

  useEffect(() => {

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenText}>Notifications:</Text>
      <View style={styles.clearButton}>
        <Button title="Clear All" onPress={clearAll} color="#bb2222" />
      </View>
      <FlatList
        data={notifications}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item, index }) => (
          <TouchableOpacity onPress={() => handleNotificationTap(item)}>
            <View style={styles.notificationBox}>
              <Text style={styles.messageText}>🪴 {item.message}</Text>
              <Text style={styles.timestampText}>{item.timestamp}</Text>
              <TouchableOpacity onPress={() => deleteOne(index)}>
                <Text style={styles.clearOne}>X  </Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        )}
      />
      {dropdownVisible && (
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Pod Number</Text>
            {[1, 2, 3, 4].map(pod => (
              <TouchableOpacity key={pod} onPress={() => handlePodSelection(pod)} style={styles.podButton}>
                <Text style={styles.podButtonText}>Pod {pod}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity onPress={() => setDropdownVisible(false)}>
              <Text style={styles.cancelButton}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );

  
}


const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    padding: 20,
    backgroundColor: '#e4dfc9',
    
  },
  screenText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: "center"
  },
  clearButton: {
    alignItems: "center",
    marginBottom: 10,
  },
  notificationBox: {
    
    padding: 15,
    backgroundColor: "#fffaf3",
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  messageText: {
    fontSize: 16,
    color: "#6c9a8b",
    flex: 1,
    marginLeft: 10,
  },
  timestampText: {
    fontSize: 13,
    color: "#777",
    marginRight: 13
  },
  clearOne: {
    marginLeft: 10,
    fontSize: 18,
    color: "#2e5339" //bb2222
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  modalContent: {
    width: 300,
    backgroundColor: '#fffaf3',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2e5339',
    marginBottom: 15,
  },
  
  podButton: {
    padding: 10,
    marginVertical: 5,
    backgroundColor: '#6c9a8b',
    borderRadius: 5,
    width: '100%',
    alignItems: 'center',
  },
  
  podButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  
  cancelButton: {
    marginTop: 10,
    color: '#a68b6d',
    fontSize: 16,
  },
  

});

export default Notification;