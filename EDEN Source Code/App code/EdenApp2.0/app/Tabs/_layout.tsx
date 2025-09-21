import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { FontAwesome5 } from "@expo/vector-icons";
import EdCalendar from "./Home";
import Pod from "./pod";
import Notification from "./Notification";
import { StyleSheet } from "react-native";


const Tab = createBottomTabNavigator();
export default function TabNav() {
  return (
    <Tab.Navigator
      screenOptions={({
        headerShown: false,
        tabBarActiveTintColor: '#6c9a8b',
        tabBarInactiveTintColor: 'grey',
        tabBarStyle: {
          backgroundColor: '#f5f3eb', // Light earthy green background
          borderTopLeftRadius: 15,
          borderTopRightRadius: 15,
          height: 60,
          borderTopWidth: 0, // Optional: removes the top border
        },

      })}
    >
      <Tab.Screen name="Calendar"
        component={EdCalendar}
        options={{
          tabBarIcon: ({ color, size }) => {
            return (
              <Ionicons name="calendar" size={size} color={color} />

            )
          }
        }} />
      <Tab.Screen name="Notifications"
        component={Notification}
        options={{
          tabBarIcon: ({ color, size }) => {
            return (
              <Ionicons name="notifications" size={size} color={color} />
            )
          }
        }}
      />
      <Tab.Screen name="Pods"
        component={Pod}
        options={{
          tabBarIcon: ({ color, size }) => {
            return (
              <FontAwesome5 name="leaf" size={size} color={color} />
            )
          }
        }}
      />
    </Tab.Navigator>
  );
};
const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  screenText: {
    fontSize: 20,
    fontWeight: 'bold',
  },

});
