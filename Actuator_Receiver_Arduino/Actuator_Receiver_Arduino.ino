
String readString, d0, d1, tempString;
int c0, c1, tempInt;
bool newData = false;
const byte numChars = 9;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

char messageFromPC[numChars] = {0};
int integerFromPC = 0;

const int cellCount = 2;
byte cells[cellCount];

int interval = 1;

const int ON = 2;
const int STROBE = 4;
const int CLOCK = 5;

const int DATA_1 = 6;
const int TEMPH = 7;
const int TEMPC = 8;


void setup() {
  pinMode(ON, OUTPUT);
  pinMode(STROBE, OUTPUT);
  pinMode(CLOCK, OUTPUT);
  
  pinMode(DATA_1, OUTPUT);
  pinMode(TEMPH, OUTPUT);
  pinMode(TEMPC, OUTPUT);

  digitalWrite(ON, LOW);

  Serial1.begin(115200);
  Serial.begin(115200);
}

void loop() {
  recvWithStartEndMarkers();
  if (newData == true) {
    strcpy(tempChars, receivedChars);

    if (strlen(tempChars) == 7) {
      strncpy(messageFromPC, tempChars, 7);
      messageFromPC[7] = '\0';

      Serial.println(messageFromPC);
      readString = messageFromPC;
      d0 = readString.substring(0, 3);
      d1 = readString.substring(3, 6);

      c0 = d0.toInt();
      c1 = d1.toInt();

      cells[0] = c0;
      cells[1] = c1;

      tempString = readString.substring(6, 7);
      tempInt = tempString.toInt();

      Flush();
      delay(interval);

      newData = false;  // Reset newData flag after processing the data
    }
  }
}


void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial1.available() > 0 && newData == false) {
    rc = Serial1.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      } else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
      ndx = 0; // Reset the index when starting to receive new data
    }
  }
}

void Flush() {
  if (tempInt == 1) {
    digitalWrite(TEMPH, HIGH);
  }else if (tempInt == 2) {
    digitalWrite(TEMPC, HIGH);
  } else {
    digitalWrite(TEMPH, LOW);
    digitalWrite(TEMPC, LOW);
  }

  const int bitOrder[8] = {6, 7, 2, 1, 0, 5, 4, 3};
  for (int i = 0; i < 2; i++){

    for (int j = 0; j < 8; j++) {
      digitalWrite(DATA_1, bitRead(cells[i], bitOrder[j]) ? LOW : HIGH);
      digitalWrite(CLOCK, HIGH);
      digitalWrite(CLOCK, LOW);
    }
  }
  digitalWrite(STROBE, HIGH);
  digitalWrite(STROBE, LOW);

  

}

