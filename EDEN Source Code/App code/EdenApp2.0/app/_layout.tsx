import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Drawer } from 'expo-router/drawer';
import { StyleSheet, Text, View } from "react-native";
import { DrawerContentScrollView, DrawerItemList } from '@react-navigation/drawer';
import { Stack } from "expo-router";
import { PlantingContext } from "./Tabs/PlantingContext"; // adjust the path if needed
import { useState } from "react";




export default function Layout() {
  const [plantingData, setPlantingData] = useState({});
  
  return (
    
    <GestureHandlerRootView style={{ flex: 1 }}>
      <PlantingContext.Provider value={{ plantingData, setPlantingData }}>
        <Drawer drawerContent={props => <CustomDrawerContent {...props} />}>
          

          
          <Drawer.Screen
            name="Tabs" 
            options={{
              drawerLabel: 'Home',
              title: 'EDEN',
              headerTitleAlign: 'center',
              headerTintColor: 'white', // changes the color of the text in eden
              headerPressColor: '#6c9a8b', 
              overlayColor: 'rgba(108, 154, 139, 0.4)', // add an opacity to this
              drawerActiveBackgroundColor: '#6c9a8b',  
              drawerActiveTintColor: 'white', 
              headerStyle: {
                backgroundColor: '#6c9a8b', 
              },
              drawerStyle: {
                backgroundColor: '#f5f3eb', // Light earthy green background to match style
                borderTopLeftRadius: 15,
                borderTopRightRadius: 15,
                
              },
            }}
          />

          <Drawer.Screen
            name="index" 
            options={{
              drawerItemStyle: { display: "none" },
              title: 'lol',
              headerTitleAlign: 'center',
              //headerTintColor: '#f5f3eb', 
              headerPressColor: '#6c9a8b', 
              overlayColor: 'rgba(108, 154, 139, 0.4)', 
              drawerActiveBackgroundColor: '#6c9a8b',  
              drawerActiveTintColor: 'white',
              drawerStyle: {
                backgroundColor: '#f5f3eb', 
                borderTopLeftRadius: 15,
                borderTopRightRadius: 15,
                
                
              },
            }}
          />
          <Drawer.Screen
            name="Settings" 
            options={{
              drawerLabel: 'Settings',
              title: 'Settings ',
              headerTitleAlign: 'center',
              //headerTintColor: '#f5f3eb', 
              headerPressColor: '#6c9a8b', 
              overlayColor: 'rgba(108, 154, 139, 0.4)', 
              drawerActiveBackgroundColor: '#6c9a8b',  
              drawerActiveTintColor: 'white',
              drawerStyle: {
                backgroundColor: '#f5f3eb', 
                borderTopLeftRadius: 15,
                borderTopRightRadius: 15,
                
                
              },
            }}


          />
          <Drawer.Screen
            name="Extras" 
            options={{
              drawerLabel: 'Help & About',
              title: 'k,bsjkzvd ',
              headerTitleAlign: 'center',
              drawerStyle: {
                backgroundColor: '#f5f3eb', 
                borderTopLeftRadius: 15,
                borderTopRightRadius: 15,
                
                
              },
              
              headerTintColor: 'white', 
              headerPressColor: '#6c9a8b', 
              overlayColor: 'rgba(108, 154, 139, 0.4)', 
              drawerActiveBackgroundColor: '#6c9a8b',  
              drawerActiveTintColor: 'white', 
              headerStyle: {
                backgroundColor: '#6c9a8b', 
              },
              
            }}


          />
        </Drawer>
      </PlantingContext.Provider>
    </GestureHandlerRootView>
  );
}


function CustomDrawerContent(props) {
  return (
    <DrawerContentScrollView {...props}>
      <View style={styles.drawerHeader}>
        <Text style={styles.drawerHeaderText}>EDEN</Text>
      </View>
      <DrawerItemList {...props} />
    </DrawerContentScrollView>
  );
}

const styles = StyleSheet.create({
  drawerHeader: {
    padding: 20,
    borderBottomWidth: 1,
    borderColor: '#f5f3eb',
    backgroundColor: '#f5f3eb',
    
  },
  drawerHeaderText: {
    textAlign: 'center',
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    backgroundColor: '#f5f3eb',
  },
});

