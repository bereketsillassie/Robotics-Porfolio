import { StyleSheet,View,Text } from "react-native";

function Extras() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenText}>Help screen</Text>
    </View>
  );
}


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
        
} );

export default Extras;