/*
  Ultrasonic Sensor HC-SR04 and Arduino Tutorial

  by Dejan Nedelkovski,
  www.HowToMechatronics.com

*/

#define PWM_MAX 255U
#define PWM_MIN 0U
#define PROFUNDIDAD 60.5

float runtimeMedirDistancia(void);
void setControlOut(int pwm);
float getAltura();
void ejecutarComando();
void runtimeOnOffUpdate();
void runtimePidUpdate();
void pidInit(int reset);
void setKp(float kp);
void setKi(float ki);
void setKd(float kd);
void setReferencia(float ref);
void setWindUp(uint8_t set);
void pidToString(void);

typedef enum
{
  openLoop = 0,    
  closeOnOff,    
  closePid
} estadosLazos_t;

uint8_t nuevoComando = 0;  

// defines pins numbers
const int trigPin = 9;
const int echoPin = 10;
const int controlOutPin = 5;
// defines variables
long duration;
int distance;
float distancia;
float entrada;
estadosLazos_t estadosDeControl = closePid;

struct DatosOnOff{
  float limiteSuperior = 75;
  float limiteInferior = 65;      
}datosOnOff;

struct DatosPID{
  float kp;
  float ki;
  float kd ;
  float referencia;
  float coeficientes[3];
  float historial[3];
  float salida;
  float limiteMaximo = 255;
  float limiteMinimo = 0;
  uint8_t windUpEstado = 1;
  }datosPid;

char comando[20];
size_t comandIdx = 0;


void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  pinMode(controlOutPin, OUTPUT);
  Serial.begin(9600); // Starts the serial communication
  Serial.setTimeout(50);
}

void loop() {

  //runtimeMedirDistancia();
  leerCommando();
  //ejecutarComando();

  /*
    switch(estadosDeControl ){
      case openLoop: 
        setControlOut(entrada); 
        break;
      case closePid:
        runtimePidUpdate();
        break;
      case closeOnOff:
        runtimeOnOffUpdate();
      break;

    } 
  */
  ////serial.println(getAltura());
  delay(1);
}


void leerCommando(){
  while (Serial.available())
  {
    char character = Serial.read();
    if (character != '\n')
    {
      comando[comandIdx] = character;
      comandIdx ++;
    }
    else
    {
      comando[comandIdx] = 0;
      comandIdx = 0;
      nuevoComando = 1;
    }
  }
  if(comando[0] == 'a')
  {
    ////serial.println("probando");
    analogWrite(controlOutPin, atoi(&comando[1]));
  }  
}

float runtimeMedirDistancia(){
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distancia = 0.99*distancia + 0.005*((float)duration * 0.034);

  return distancia;
}

float getAltura(){
  return PROFUNDIDAD - distancia;
}

void setControlOut(int pwm){
  if( pwm < PWM_MIN)  
    pwm = PWM_MIN;
  else if (pwm > PWM_MAX)
    pwm = PWM_MAX;
    
  analogWrite(controlOutPin, pwm);
}

void ejecutarComando(){
  if(nuevoComando == 1){
    switch(comando[0]){
      case 'V':
      case 'v':
        entrada = atof(&comando[1]);
        //serial.print(getAltura());
        //serial.print(", ");
        //serial.println( entrada);
      break; 
      case 'M':
        estadosDeControl = openLoop;
        //serial.println("lazo abierto establecido");
      break;    
      case 'D':
        estadosDeControl = closeOnOff;
        //serial.println("lazo on/off establecido");
      break;    
      case 'a':
        //serial.print("altura: ");
        //serial.println(getAltura());
        //serial.print("salida: ");
        //serial.println(datosPid.salida);
      break;    
      case 'k':
      case 'K':
        estadosDeControl = closePid;
        float valor = atof(&comando[2]);
        switch(comando[1]){      
          case 'p':
          case 'P':
            setKp(valor);
          break;
          case 'i':
          case 'I':
            setKi(valor);
          break;
          case 'd':
          case 'D':
            setKd(valor);
          break;
          case 'r':
          case 'R':
            setReferencia(valor);
          break;       
          case 'w':
          case 'W':
          setWindUp(valor);
          break;       
        }
        //serial.println("lazo pid establecido");
        pidToString();
        break;
      }
    nuevoComando = 0;
  }
}

void runtimeOnOffUpdate(){
  if(getAltura() > datosOnOff.limiteSuperior){
    setControlOut(0);
    }
  else if(getAltura() < datosOnOff.limiteInferior){
    setControlOut(255);
    }
}

void runtimePidUpdate(){
  float error = datosPid.referencia - getAltura();
  datosPid.historial[2] = datosPid.historial[1];
  datosPid.historial[1] = datosPid.historial[0];
  datosPid.historial[0] = error;

  for(uint8_t i = 0 ; i < 3 ; i++){
    datosPid.salida += datosPid.coeficientes[i] * datosPid.historial[i];
  }

  if(datosPid.windUpEstado != 0){
    if(datosPid.salida < datosPid.limiteMinimo){
      datosPid.salida = datosPid.limiteMinimo;     
    }    
    else if(datosPid.salida > datosPid.limiteMaximo){
      datosPid.salida = datosPid.limiteMaximo;
    }    
  }

  setControlOut(datosPid.salida);
}

void pidInit(int reset){
  datosPid.coeficientes[0] = datosPid.kp + datosPid.ki + datosPid.kd;
  datosPid.coeficientes[1] = (-datosPid.kp ) - (2 * datosPid.kd );
  datosPid.coeficientes[2] = datosPid.kd;
  if(reset){
    datosPid.salida = 0;
  }
}

void setKp(float kp){
  datosPid.kp = kp;
  pidInit(0);
}

void setKi(float ki){
  datosPid.ki = ki;  
  pidInit(0);
}

void setKd(float kd){
  datosPid.kd = kd;
  pidInit(0);
}

void setReferencia(float ref){
  datosPid.referencia = ref;
}

void setWindUp(uint8_t set){
  datosPid.windUpEstado = set;
}

void pidToString(){
  //serial.print("Kp: ");
  //serial.println(datosPid.kp);
  //serial.print("Ki: ");
  //serial.println(datosPid.ki);
  //serial.print("Kd: ");
  //serial.println(datosPid.kd);
  //serial.print("Referencia: ");
  //serial.println(datosPid.referencia);
  //serial.print("Salida: ");
  //serial.println(datosPid.salida);
  //serial.print("WD: ");
  //serial.println(datosPid.windUpEstado);
  //serial.print("estado: ");
  if(estadosDeControl == closePid){
    //serial.println("Encendido");
  }else{
    //serial.println("Encendido");
  }
}
