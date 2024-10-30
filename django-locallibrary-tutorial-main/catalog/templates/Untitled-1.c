#include <reg51.h>

void delay_ms(unsigned int time){

	int i,j;
	for (i = 0; i < time; i++){
		for(j = 0; j < 123; j++){
		}
	}
}

char arr1[5] = "by ";
	
int main(){
	int i;
	SCON = 0x50;
	TMOD = 0x20;
	TH1 = 253;
	TR1 = 1;
	
	while(1)
	{
			SBUF = 'a';
			while(TI==0);
			delay_ms(5000);
			TI = 0;
	}
}
