/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "fatfs.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdio.h"
#include "string.h"
#include "wav.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define ADCBUFLEN 32768
#define BUFFER_FULL 1
#define BUFFER_EMPTY 0
#define MILLISECS_TO_RECORD 500
#define ACQ_FILENAME "WAV37.DAT"
#define RECORD 0x01
#define STOP 0x02
#define DATETIME 0x03
#define LOCATION  0x04
#define SAVE 0x05

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

RTC_HandleTypeDef hrtc;

SD_HandleTypeDef hsd1;

SPI_HandleTypeDef hspi6;

UART_HandleTypeDef huart3;

MDMA_HandleTypeDef hmdma_mdma_channel40_sdmmc1_end_data_0;
/* USER CODE BEGIN PV */

uint32_t bytes_written=0;
uint32_t bytes_read=0;
uint32_t bytes_read2=1;
uint32_t total_bytes_written=0;
uint32_t total_blocks_written=0;
uint32_t read_value=0;
uint32_t adcbuf_index=0;

FRESULT result; /* FatFs function common result code */

uint16_t adc_buf[ADCBUFLEN];
int adc_lower_status = BUFFER_EMPTY;
int adc_upper_status = BUFFER_EMPTY;
uint32_t end_acq_ms;

char spi_buf[20];
int SPI6_NCS;

struct wavfile_header_s wavfile_header_t;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
void PeriphCommonClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_MDMA_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_SDMMC1_SD_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_SPI6_Init(void);
static void MX_RTC_Init(void);
/* USER CODE BEGIN PFP */
void Acquire_ADC_Data();
FRESULT scan_files (char* path);
FRESULT print_file(char *filename);
int write_wav_header(int32_t SampleRate,int32_t FrameCount);
FRESULT print_file_values(char *filename );

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void)
{
	/* USER CODE BEGIN 1 */
	/* ADC Testing and writing to SD Card*/
	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* Configure the peripherals common clocks */
	PeriphCommonClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_MDMA_Init();
	MX_DMA_Init();
	MX_ADC1_Init();
	MX_SDMMC1_SD_Init();
	MX_FATFS_Init();
	MX_USART3_UART_Init();
	MX_SPI6_Init();
	MX_RTC_Init();
	/* USER CODE BEGIN 2 */

	printf("\r\nProgram Start\r\n");

	RTC_DateTypeDef gDate;
	RTC_TimeTypeDef gTime;

	int previous_cs=HAL_GPIO_ReadPin (SPI6_NCS_GPIO_Port, SPI6_NCS_Pin);
	int current_cs = previous_cs;
	for(;;){
		current_cs=HAL_GPIO_ReadPin (SPI6_NCS_GPIO_Port, SPI6_NCS_Pin);
		if(previous_cs && !current_cs){
			HAL_SPI_Receive(&hspi6, (uint8_t *)spi_buf, 10, 100);
			printf("%02x %02x %02x %02x %02x %02x %02x %02x %02x\r\n",spi_buf[0],spi_buf[1],spi_buf[2],spi_buf[3],spi_buf[4],spi_buf[5],spi_buf[6],spi_buf[7],spi_buf[8]);
			switch(spi_buf[0]){
			case RECORD:
				printf("Record: Sampling %3dkHz  Gain %1d   FILE%04d.DAT\r\n", spi_buf[1]*256+spi_buf[2], spi_buf[3], spi_buf[4]*256+spi_buf[5]);
				break;
			case STOP:
				printf("Stop\r\n");
				HAL_RTC_GetTime(&hrtc, &gTime, RTC_FORMAT_BIN);
				/* Get the RTC current Date */
				HAL_RTC_GetDate(&hrtc, &gDate, RTC_FORMAT_BIN);
				/* Display time Format: hh:mm:ss */
				printf("RTC Date Time    ");
				printf("%02d:%02d:%02d   ",gTime.Hours, gTime.Minutes, gTime.Seconds);
				/* Display date Format: dd-mm-yy */
				printf("%02d-%02d-%2d\r\n",gDate.Month,gDate.Date,2000 + gDate.Year);
				break;
			case DATETIME:
				printf("");
				RTC_TimeTypeDef sTime;
				RTC_DateTypeDef sDate;
				sTime.Hours = spi_buf[1]; // set hours
				sTime.Minutes = spi_buf[2]; // set minutes
				sTime.Seconds = spi_buf[3]; // set seconds
				sTime.DayLightSaving = RTC_DAYLIGHTSAVING_NONE;
				sTime.StoreOperation = RTC_STOREOPERATION_RESET;
				if (HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BIN) != HAL_OK)
				{
					printf("problem setting time\r\n");
				}
				sDate.WeekDay = 4;
				sDate.Month = spi_buf[5];
				sDate.Date = spi_buf[6]; // date
				sDate.Year = spi_buf[7]*256+spi_buf[8]-2000; // year
				if (HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BIN) != HAL_OK)
				{
					printf("problem setting date\r\n");
				}
				HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, 0x32F2); // backup register
				break;
			case LOCATION:
				printf("Location\r\n");
				break;
			case SAVE:
				printf("Save\r\n");
				break;
			}
		}
		previous_cs=current_cs;
	}


	char buff[256];
	printf("Mounting SD Card\r\n");
	if(f_mount(&SDFatFS, (TCHAR const*)SDPath, 0) != FR_OK)
	{
		Error_Handler();
	}
	else
	{
		//	  HAL_Delay(1000);
		printf("SD Card Directory Before\r\n");
		strcpy(buff, "/");
		result = scan_files(buff);

		//Open file for writing (Create)
		printf("Opening File for writing\r\n");
		if(f_open(&SDFile, ACQ_FILENAME, FA_CREATE_ALWAYS | FA_WRITE) != FR_OK)
		{
			Error_Handler();
		}
		else
		{
			printf("Writing WAV Header\r\n");
			write_wav_header(786000,786000); // Sampling at 786000 Hz for 100mS

			printf("Clearing ADC Buffer\r\n");
			for(adcbuf_index=0;adcbuf_index < ADCBUFLEN;adcbuf_index++)
			{
				adc_buf[adcbuf_index]=0;
			}

			printf("Enable ADC DMA and add contents\r\n");
			HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buf, ADCBUFLEN);

			printf("Acquiring ADC Data\r\n");
			Acquire_ADC_Data();

			printf("Halting ADC DMA \r\n");
			HAL_ADC_Stop_DMA(&hadc1);

			printf("Writing Complete\r\n");
			f_close(&SDFile);

			printf("Total Blocks Written %d\r\n",total_blocks_written);
			printf("Total Bytes Written %d\r\n",total_bytes_written);
			//		  printf("File Contents\r\n");
			print_file(ACQ_FILENAME);

			printf("SD Card Directory After 1\r\n");
			strcpy(buff, "/");
			result = scan_files(buff);

			f_mount(0, "", 0);

			// print analog values from file
			printf("Opening File for Content Examination\r\n");
			//		  print_file_values(ACQ_FILENAME);
			int i,min,max;
			min=adc_buf[10];
			max=adc_buf[10];
			for(i=0;i<32760;i++){
				if(adc_buf[i]<min){
					min =adc_buf[i];
				}
				if(adc_buf[i]>max){
					max=adc_buf[i];
				}
			}
			printf("Min %x %d    Max %x %d\r\n",min,min,max,max);

		}
	}
	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */

	/* USER CODE END WHILE */

	/* USER CODE BEGIN 3 */

	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void)
{
	RCC_OscInitTypeDef RCC_OscInitStruct = {0};
	RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

	/** Supply configuration update enable
	 */
	HAL_PWREx_ConfigSupply(PWR_DIRECT_SMPS_SUPPLY);

	/** Configure the main internal regulator output voltage
	 */
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

	while(!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI|RCC_OSCILLATORTYPE_LSI
			|RCC_OSCILLATORTYPE_HSE;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.HSIState = RCC_HSI_DIV1;
	RCC_OscInitStruct.HSICalibrationValue = 64;
	RCC_OscInitStruct.LSIState = RCC_LSI_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM = 5;
	RCC_OscInitStruct.PLL.PLLN = 160;
	RCC_OscInitStruct.PLL.PLLP = 2;
	RCC_OscInitStruct.PLL.PLLQ = 4;
	RCC_OscInitStruct.PLL.PLLR = 1;
	RCC_OscInitStruct.PLL.PLLRGE = RCC_PLL1VCIRANGE_2;
	RCC_OscInitStruct.PLL.PLLVCOSEL = RCC_PLL1VCOWIDE;
	RCC_OscInitStruct.PLL.PLLFRACN = 0;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
	{
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
			|RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2
			|RCC_CLOCKTYPE_D3PCLK1|RCC_CLOCKTYPE_D1PCLK1;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.SYSCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB3CLKDivider = RCC_APB3_DIV2;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_APB1_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_APB2_DIV2;
	RCC_ClkInitStruct.APB4CLKDivider = RCC_APB4_DIV2;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
	{
		Error_Handler();
	}
}

/**
 * @brief Peripherals Common Clock Configuration
 * @retval None
 */
void PeriphCommonClock_Config(void)
{
	RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};

	/** Initializes the peripherals clock
	 */
	PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_CKPER;
	PeriphClkInitStruct.CkperClockSelection = RCC_CLKPSOURCE_HSI;
	if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct) != HAL_OK)
	{
		Error_Handler();
	}
}

/**
 * @brief ADC1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_ADC1_Init(void)
{

	/* USER CODE BEGIN ADC1_Init 0 */

	/* USER CODE END ADC1_Init 0 */

	ADC_MultiModeTypeDef multimode = {0};
	ADC_ChannelConfTypeDef sConfig = {0};

	/* USER CODE BEGIN ADC1_Init 1 */

	/* USER CODE END ADC1_Init 1 */

	/** Common config
	 */
	hadc1.Instance = ADC1;
	hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV4;
	hadc1.Init.Resolution = ADC_RESOLUTION_16B;
	hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
	hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
	hadc1.Init.LowPowerAutoWait = DISABLE;
	hadc1.Init.ContinuousConvMode = ENABLE;
	hadc1.Init.NbrOfConversion = 1;
	hadc1.Init.DiscontinuousConvMode = DISABLE;
	hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
	hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
	hadc1.Init.ConversionDataManagement = ADC_CONVERSIONDATA_DMA_CIRCULAR;
	hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
	hadc1.Init.LeftBitShift = ADC_LEFTBITSHIFT_NONE;
	hadc1.Init.OversamplingMode = DISABLE;
	if (HAL_ADC_Init(&hadc1) != HAL_OK)
	{
		Error_Handler();
	}

	/** Configure the ADC multi-mode
	 */
	multimode.Mode = ADC_MODE_INDEPENDENT;
	if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK)
	{
		Error_Handler();
	}

	/** Configure Regular Channel
	 */
	sConfig.Channel = ADC_CHANNEL_2;
	sConfig.Rank = ADC_REGULAR_RANK_1;
	sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;
	sConfig.SingleDiff = ADC_SINGLE_ENDED;
	sConfig.OffsetNumber = ADC_OFFSET_NONE;
	sConfig.Offset = 0;
	sConfig.OffsetSignedSaturation = DISABLE;
	if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
	{
		Error_Handler();
	}
	/* USER CODE BEGIN ADC1_Init 2 */

	/* USER CODE END ADC1_Init 2 */

}

/**
 * @brief RTC Initialization Function
 * @param None
 * @retval None
 */
static void MX_RTC_Init(void)
{

	/* USER CODE BEGIN RTC_Init 0 */

	/* USER CODE END RTC_Init 0 */

	RTC_TimeTypeDef sTime = {0};
	RTC_DateTypeDef sDate = {0};

	/* USER CODE BEGIN RTC_Init 1 */

	/* USER CODE END RTC_Init 1 */

	/** Initialize RTC Only
	 */
	hrtc.Instance = RTC;
	hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
	hrtc.Init.AsynchPrediv = 127;
	hrtc.Init.SynchPrediv = 255;
	hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
	hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
	hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
	hrtc.Init.OutPutRemap = RTC_OUTPUT_REMAP_NONE;
	if (HAL_RTC_Init(&hrtc) != HAL_OK)
	{
		Error_Handler();
	}

	/* USER CODE BEGIN Check_RTC_BKUP */

	/* USER CODE END Check_RTC_BKUP */

	/** Initialize RTC and set the Time and Date
	 */
	sTime.Hours = 0x0;
	sTime.Minutes = 0x0;
	sTime.Seconds = 0x0;
	sTime.DayLightSaving = RTC_DAYLIGHTSAVING_NONE;
	sTime.StoreOperation = RTC_STOREOPERATION_RESET;
	if (HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BCD) != HAL_OK)
	{
		Error_Handler();
	}
	sDate.WeekDay = RTC_WEEKDAY_MONDAY;
	sDate.Month = RTC_MONTH_JANUARY;
	sDate.Date = 0x1;
	sDate.Year = 0x0;

	if (HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BCD) != HAL_OK)
	{
		Error_Handler();
	}
	/* USER CODE BEGIN RTC_Init 2 */

	/* USER CODE END RTC_Init 2 */

}

/**
 * @brief SDMMC1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_SDMMC1_SD_Init(void)
{

	/* USER CODE BEGIN SDMMC1_Init 0 */

	/* USER CODE END SDMMC1_Init 0 */

	/* USER CODE BEGIN SDMMC1_Init 1 */

	/* USER CODE END SDMMC1_Init 1 */
	hsd1.Instance = SDMMC1;
	hsd1.Init.ClockEdge = SDMMC_CLOCK_EDGE_RISING;
	hsd1.Init.ClockPowerSave = SDMMC_CLOCK_POWER_SAVE_DISABLE;
	hsd1.Init.BusWide = SDMMC_BUS_WIDE_4B;
	hsd1.Init.HardwareFlowControl = SDMMC_HARDWARE_FLOW_CONTROL_DISABLE;
	hsd1.Init.ClockDiv = 2;
	/* USER CODE BEGIN SDMMC1_Init 2 */

	/* USER CODE END SDMMC1_Init 2 */

}

/**
 * @brief SPI6 Initialization Function
 * @param None
 * @retval None
 */
static void MX_SPI6_Init(void)
{

	/* USER CODE BEGIN SPI6_Init 0 */

	/* USER CODE END SPI6_Init 0 */

	/* USER CODE BEGIN SPI6_Init 1 */

	/* USER CODE END SPI6_Init 1 */
	/* SPI6 parameter configuration*/
	hspi6.Instance = SPI6;
	hspi6.Init.Mode = SPI_MODE_SLAVE;
	hspi6.Init.Direction = SPI_DIRECTION_2LINES;
	hspi6.Init.DataSize = SPI_DATASIZE_8BIT;
	hspi6.Init.CLKPolarity = SPI_POLARITY_LOW;
	hspi6.Init.CLKPhase = SPI_PHASE_1EDGE;
	hspi6.Init.NSS = SPI_NSS_SOFT;
	hspi6.Init.FirstBit = SPI_FIRSTBIT_MSB;
	hspi6.Init.TIMode = SPI_TIMODE_DISABLE;
	hspi6.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
	hspi6.Init.CRCPolynomial = 0x0;
	hspi6.Init.NSSPMode = SPI_NSS_PULSE_DISABLE;
	hspi6.Init.NSSPolarity = SPI_NSS_POLARITY_LOW;
	hspi6.Init.FifoThreshold = SPI_FIFO_THRESHOLD_01DATA;
	hspi6.Init.TxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
	hspi6.Init.RxCRCInitializationPattern = SPI_CRC_INITIALIZATION_ALL_ZERO_PATTERN;
	hspi6.Init.MasterSSIdleness = SPI_MASTER_SS_IDLENESS_00CYCLE;
	hspi6.Init.MasterInterDataIdleness = SPI_MASTER_INTERDATA_IDLENESS_00CYCLE;
	hspi6.Init.MasterReceiverAutoSusp = SPI_MASTER_RX_AUTOSUSP_DISABLE;
	hspi6.Init.MasterKeepIOState = SPI_MASTER_KEEP_IO_STATE_DISABLE;
	hspi6.Init.IOSwap = SPI_IO_SWAP_DISABLE;
	if (HAL_SPI_Init(&hspi6) != HAL_OK)
	{
		Error_Handler();
	}
	/* USER CODE BEGIN SPI6_Init 2 */

	/* USER CODE END SPI6_Init 2 */

}

/**
 * @brief USART3 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART3_UART_Init(void)
{

	/* USER CODE BEGIN USART3_Init 0 */

	/* USER CODE END USART3_Init 0 */

	/* USER CODE BEGIN USART3_Init 1 */

	/* USER CODE END USART3_Init 1 */
	huart3.Instance = USART3;
	huart3.Init.BaudRate = 576000;
	huart3.Init.WordLength = UART_WORDLENGTH_8B;
	huart3.Init.StopBits = UART_STOPBITS_1;
	huart3.Init.Parity = UART_PARITY_NONE;
	huart3.Init.Mode = UART_MODE_TX_RX;
	huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart3.Init.OverSampling = UART_OVERSAMPLING_16;
	huart3.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
	huart3.Init.ClockPrescaler = UART_PRESCALER_DIV1;
	huart3.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
	if (HAL_UART_Init(&huart3) != HAL_OK)
	{
		Error_Handler();
	}
	if (HAL_UARTEx_SetTxFifoThreshold(&huart3, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
	{
		Error_Handler();
	}
	if (HAL_UARTEx_SetRxFifoThreshold(&huart3, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
	{
		Error_Handler();
	}
	if (HAL_UARTEx_DisableFifoMode(&huart3) != HAL_OK)
	{
		Error_Handler();
	}
	/* USER CODE BEGIN USART3_Init 2 */

	/* USER CODE END USART3_Init 2 */

}

/**
 * Enable DMA controller clock
 */
static void MX_DMA_Init(void)
{

	/* DMA controller clock enable */
	__HAL_RCC_DMA1_CLK_ENABLE();

	/* DMA interrupt init */
	/* DMA1_Stream0_IRQn interrupt configuration */
	HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(DMA1_Stream0_IRQn);

}

/**
 * Enable MDMA controller clock
 * Configure MDMA for global transfers
 *   hmdma_mdma_channel40_sdmmc1_end_data_0
 */
static void MX_MDMA_Init(void)
{

	/* MDMA controller clock enable */
	__HAL_RCC_MDMA_CLK_ENABLE();
	/* Local variables */

	/* Configure MDMA channel MDMA_Channel0 */
	/* Configure MDMA request hmdma_mdma_channel40_sdmmc1_end_data_0 on MDMA_Channel0 */
	hmdma_mdma_channel40_sdmmc1_end_data_0.Instance = MDMA_Channel0;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.Request = MDMA_REQUEST_SDMMC1_END_DATA;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.TransferTriggerMode = MDMA_BUFFER_TRANSFER;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.Priority = MDMA_PRIORITY_LOW;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.Endianness = MDMA_LITTLE_ENDIANNESS_PRESERVE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.SourceInc = MDMA_SRC_INC_BYTE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.DestinationInc = MDMA_DEST_INC_BYTE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.SourceDataSize = MDMA_SRC_DATASIZE_BYTE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.DestDataSize = MDMA_DEST_DATASIZE_BYTE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.DataAlignment = MDMA_DATAALIGN_PACKENABLE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.BufferTransferLength = 1;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.SourceBurst = MDMA_SOURCE_BURST_SINGLE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.DestBurst = MDMA_DEST_BURST_SINGLE;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.SourceBlockAddressOffset = 0;
	hmdma_mdma_channel40_sdmmc1_end_data_0.Init.DestBlockAddressOffset = 0;
	if (HAL_MDMA_Init(&hmdma_mdma_channel40_sdmmc1_end_data_0) != HAL_OK)
	{
		Error_Handler();
	}

	/* Configure post request address and data masks */
	if (HAL_MDMA_ConfigPostRequestMask(&hmdma_mdma_channel40_sdmmc1_end_data_0, 0, 0) != HAL_OK)
	{
		Error_Handler();
	}

	/* MDMA interrupt initialization */
	/* MDMA_IRQn interrupt configuration */
	HAL_NVIC_SetPriority(MDMA_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(MDMA_IRQn);

}

/**
 * @brief GPIO Initialization Function
 * @param None
 * @retval None
 */
static void MX_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};
	/* USER CODE BEGIN MX_GPIO_Init_1 */
	/* USER CODE END MX_GPIO_Init_1 */

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOD_CLK_ENABLE();
	__HAL_RCC_GPIOF_CLK_ENABLE();
	__HAL_RCC_GPIOH_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(RED_LED_GPIO_Port, RED_LED_Pin, GPIO_PIN_RESET);

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(Sync_GPIO_Port, Sync_Pin, GPIO_PIN_RESET);

	/*Configure GPIO pin : RED_LED_Pin */
	GPIO_InitStruct.Pin = RED_LED_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(RED_LED_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : SPI6_NCS_Pin */
	GPIO_InitStruct.Pin = SPI6_NCS_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	HAL_GPIO_Init(SPI6_NCS_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : SD_CARD_DETECT_Pin */
	GPIO_InitStruct.Pin = SD_CARD_DETECT_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_PULLDOWN;
	HAL_GPIO_Init(SD_CARD_DETECT_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : Sync_Pin */
	GPIO_InitStruct.Pin = Sync_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(Sync_GPIO_Port, &GPIO_InitStruct);

	/* USER CODE BEGIN MX_GPIO_Init_2 */
	/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
int _write(int file, char *ptr, int len)
{
	(void)file;
	int DataIdx;

	for (DataIdx = 0; DataIdx < len; DataIdx++)
	{
		HAL_UART_Transmit(&huart3,(uint8_t*)ptr++,1,1);// Sending in normal mode
	}
	return len;
}

void Acquire_ADC_Data()
{

	end_acq_ms=uwTick+MILLISECS_TO_RECORD;
	while(1)
	{
		if(adc_lower_status == BUFFER_FULL)
		{
			result = f_write(&SDFile, &adc_buf[0], ADCBUFLEN, (void *)&bytes_written);
			if((bytes_written == 0) || (result != FR_OK))
			{
				Error_Handler();
			}
			total_bytes_written = total_bytes_written+bytes_written;
			adc_lower_status = BUFFER_EMPTY;
			HAL_GPIO_WritePin(Sync_GPIO_Port, Sync_Pin, GPIO_PIN_SET);
			total_blocks_written++;
		}
		if(adc_upper_status == BUFFER_FULL)
		{
			result = f_write(&SDFile, &adc_buf[ADCBUFLEN/2], ADCBUFLEN, (void *)&bytes_written);
			if((bytes_written == 0) || (result != FR_OK))
			{
				Error_Handler();
			}
			total_bytes_written = total_bytes_written+bytes_written;
			adc_upper_status = BUFFER_EMPTY;
			HAL_GPIO_WritePin(Sync_GPIO_Port, Sync_Pin, GPIO_PIN_RESET);
			total_blocks_written++;
		}
		if(uwTick> end_acq_ms)
		{
			return;
		}
	}
}


void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc)
{
	HAL_GPIO_WritePin(Sync_GPIO_Port, Sync_Pin, GPIO_PIN_SET);
	adc_lower_status = BUFFER_FULL;
	if(adc_upper_status == BUFFER_FULL)  // Overflow detect
	{
		HAL_GPIO_WritePin(RED_LED_GPIO_Port, RED_LED_Pin, GPIO_PIN_SET);
	}
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
	HAL_GPIO_WritePin(Sync_GPIO_Port, Sync_Pin, GPIO_PIN_RESET);
	adc_upper_status = BUFFER_FULL;
	if(adc_lower_status == BUFFER_FULL)  // Overflow detect
	{
		HAL_GPIO_WritePin(RED_LED_GPIO_Port, RED_LED_Pin, GPIO_PIN_SET);
	}
	//
}

FRESULT scan_files (
		char* path        /* Start node to be scanned (***also used as work area***) */
)
{
	FRESULT res;
	DIR dir;
	UINT i;
	static FILINFO fno;
	long filesize;

	res = f_opendir(&dir, path);                       /* Open the directory */
	if (res == FR_OK) {
		for (;;) {
			res = f_readdir(&dir, &fno);                   /* Read a directory item */
			if (res != FR_OK || fno.fname[0] == 0) break;  /* Break on error or end of dir */
			if (fno.fattrib & AM_DIR) {                    /* It is a directory */
				i = strlen(path);
				sprintf(&path[i], "/%s", fno.fname);
				res = scan_files(path);                    /* Enter the directory */
				if (res != FR_OK) break;
				path[i] = 0;
			} else {                                       /* It is a file. */
				filesize=fno.fsize;
				printf("%s/%s %ld\r\n", path, fno.fname,filesize);
				//            	if(fno.fname == "WAV15.DAT")
				//            		printf("at WAV15\r\n");
			}
		}
		f_closedir(&dir);
	}

	return res;
}

FRESULT print_file_values(char *filename )
{
	if(f_open(&SDFile, filename, FA_READ) != FR_OK)
	{
		Error_Handler();
	}
	else
	{
		uint32_t samples =22000;
		uint32_t k;
		struct wavfile_header_s wav_header;

		// Read out the header
		result = f_read(&SDFile, &wav_header,sizeof(wavfile_header_t) , (void *)&bytes_read);
		if((bytes_read == 0) || (result != FR_OK))
		{
			Error_Handler();
		}
		else
		{
			printf("WAV File Header read out \r\n");
		}


		for (k=0;k<samples;k++)
		{
			result = f_read(&SDFile, &read_value,2 , (void *)&bytes_read);
			if((bytes_read == 0) || (result != FR_OK))
			{
				Error_Handler();
			}
			else
			{
				printf("%d \r\n",read_value);
			}
		}
	}
	f_close(&SDFile);
	return FR_OK;
}

FRESULT print_file(char *filename )
{
	char read_buff[16];
	uint32_t row_address =0;
	uint32_t this_byte=0;
	char this_character;

	if(f_open(&SDFile, filename, FA_READ) != FR_OK)
	{
		Error_Handler();
	}
	else
	{
		for(row_address=0;row_address<128;row_address=row_address+16)
		{
			result = f_read(&SDFile, &read_buff,16 , (void *)&bytes_read);
			if ((bytes_read == 0) || (result != FR_OK))
			{
				Error_Handler();
			}
			else
			{
				printf("%08X ",(unsigned int)row_address);
				for(this_byte=0;this_byte<16;this_byte=this_byte+1)
				{
					printf("%02X ", read_buff[this_byte]);
				}
				printf(" ");
				for(this_byte=0;this_byte<16;this_byte=this_byte+1)
				{
					this_character = (char)read_buff[this_byte];
					if((this_character < 32 ) || (this_character>127))
					{
						this_character='.';
					}
					printf("%c ", this_character);
				}
				printf(" ");
				printf("\r\n");
			}
		}
		f_close(&SDFile);
	}
	return result;
}

/*
 * Function to write header of WAV file
 */
/*Return 0 on success and -1 on failure*/
int write_wav_header(int32_t SampleRate,int32_t FrameCount)
{
	int ret=0;

	struct wavfile_header_s wav_header;
	int32_t subchunk2_size;
	int32_t chunk_size;

	//    size_t write_count;

	uint32_t bytes_written=0;

	FRESULT result; /* FatFs function common result code */

	subchunk2_size  = FrameCount * NUM_CHANNELS * BITS_PER_SAMPLE / 8;
	chunk_size      = 4 + (8 + SUBCHUNK1SIZE) + (8 + subchunk2_size);

	wav_header.ChunkID[0] = 'R';
	wav_header.ChunkID[1] = 'I';
	wav_header.ChunkID[2] = 'F';
	wav_header.ChunkID[3] = 'F';

	wav_header.ChunkSize = chunk_size;

	wav_header.Format[0] = 'W';
	wav_header.Format[1] = 'A';
	wav_header.Format[2] = 'V';
	wav_header.Format[3] = 'E';

	wav_header.Subchunk1ID[0] = 'f';
	wav_header.Subchunk1ID[1] = 'm';
	wav_header.Subchunk1ID[2] = 't';
	wav_header.Subchunk1ID[3] = ' ';

	wav_header.Subchunk1Size = SUBCHUNK1SIZE;
	wav_header.AudioFormat = AUDIO_FORMAT;
	wav_header.NumChannels = NUM_CHANNELS;
	wav_header.SampleRate = SampleRate;
	wav_header.ByteRate = BYTE_RATE;
	wav_header.BlockAlign = BLOCK_ALIGN;
	wav_header.BitsPerSample = BITS_PER_SAMPLE;

	wav_header.Subchunk2ID[0] = 'd';
	wav_header.Subchunk2ID[1] = 'a';
	wav_header.Subchunk2ID[2] = 't';
	wav_header.Subchunk2ID[3] = 'a';
	wav_header.Subchunk2Size = subchunk2_size;

	//Open file for writing (Create)
	result = f_write(&SDFile, &wav_header, sizeof(wavfile_header_t), (void *)&bytes_written);
	if((bytes_written == 0) || (result != FR_OK))
	{
		Error_Handler();
	}

	// Flush the file buffers
	result = f_sync(&SDFile);
	if(result != FR_OK)
	{
		Error_Handler();
	}
	return ret;
}

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void)
{
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1)
	{
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
 * @brief  Reports the name of the source file and the source line number
 *         where the assert_param error has occurred.
 * @param  file: pointer to the source file name
 * @param  line: assert_param error line source number
 * @retval None
 */
void assert_failed(uint8_t *file, uint32_t line)
{
	/* USER CODE BEGIN 6 */
	/* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
	/* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
