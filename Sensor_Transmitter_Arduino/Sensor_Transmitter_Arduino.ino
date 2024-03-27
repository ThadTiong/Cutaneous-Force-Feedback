// Define pins for rows and columns
const int numRows = 4;
const int numCols = 4;
const int colPins[numRows] = { A0, A1, A2, A3 };
const int rowPins[numCols] = { A4, A5, A6, A7  };

int readings[numRows][numCols];
int thresholds[] = {50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180};
int currentThresholdIndex = 0;

int threshold;

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
}

void loop() {

  threshold = thresholds[currentThresholdIndex];

  // Iterate over each row
  for (int i = 0; i < numRows; i++) {
    // Set current row pin as OUTPUT and HIGH
    pinMode(rowPins[i], OUTPUT);
    digitalWrite(rowPins[i], HIGH);

    // Iterate over each column
    for (int j = 0; j < numCols; j++) {
      // Set current column pin as INPUT
      pinMode(colPins[j], INPUT);

      // Read analog value from current point
      readings[i][j] = analogRead(colPins[j]);

      // Set column pin back to OUTPUT and LOW
      pinMode(colPins[j], OUTPUT);
      digitalWrite(colPins[j], LOW);
    }

    // Set row pin back to INPUT
    pinMode(rowPins[i], INPUT);
  }

  sendData();
  // Display readings in a grid
  for (int i = 0; i < numRows; i++) {
    for (int j = 0; j < numCols; j++) {
      if (readings[i][j] > 100) {
        Serial.print(readings[i][j]);
      } else{
        Serial.print("0");
      }
      if (j < numCols - 1) {
        Serial.print(", ");
      }
    }
    Serial.print(", ");
  }

  // Clear serial monitor
  Serial.println();

  // Move to the next threshold index
  currentThresholdIndex = (currentThresholdIndex + 1) % (sizeof(thresholds) / sizeof(thresholds[0]));
}

String previousMsg = "";

void sendData() {
  int cell_0 = 0;
  int cell_1 = 0;

  for (int i = 0; i < numRows; i++) {
    for (int j = 0; j < numCols; j++) {
      if (readings[i][j] >= threshold) {
        if (i == 0 && j == 0) { cell_1 += 128; }
        if (i == 0 && j == 1) { cell_1 += 32; }
        if (i == 0 && j == 2) { cell_1 += 16; }
        if (i == 0 && j == 3) { cell_1 += 8; }
        if (i == 1 && j == 0) { cell_1 += 64; }
        if (i == 1 && j == 1) { cell_1 += 4; }
        if (i == 1 && j == 2) { cell_1 += 2; }
        if (i == 1 && j == 3) { cell_1 += 1; }
        if (i == 2 && j == 0) { cell_0 += 128; }
        if (i == 2 && j == 1) { cell_0 += 32; }
        if (i == 2 && j == 2) { cell_0 += 16; }
        if (i == 2 && j == 3) { cell_0 += 8; }
        if (i == 3 && j == 0) { cell_0 += 64; }
        if (i == 3 && j == 1) { cell_0 += 4; }
        if (i == 3 && j == 2) { cell_0 += 2; }
        if (i == 3 && j == 3) { cell_0 += 1; }
      }
    }
  }
  String cell_0_padded = zeroPad(cell_0, 3);
  String cell_1_padded = zeroPad(cell_1, 3);
  String msg = "<" + cell_0_padded + cell_1_padded + ">";

  if (!msg.equals(previousMsg)) {
    Serial1.println(msg);
    //Serial.println(msg);
    previousMsg = msg;
  }
}

String zeroPad(int num, int width) {
  String padded = String(num);
  while (padded.length() < width) {
    padded = "0" + padded;
  }
  return padded;
}
