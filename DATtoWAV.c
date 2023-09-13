#include <stdio.h>
#include "wav.h"

// #define BLOCKSIZE 100
#define READFILENAME "C:/Users/klapl/OneDrive/Documents/BARN/Acoustic Listening/WAV29.DAT"
#define WRITEFILENAME "C:/Users/klapl/OneDrive/Documents/BARN/Acoustic Listening/WAV29.WAV"

int main()
{
    FILE *readfileptr, *writefileptr;
    unsigned int ADC_Value;
    int Adjusted_ADC_Value;
    struct wavfile_header_s wavfile_header_t;

    // Open a file in read mode
    readfileptr = fopen(READFILENAME, "rb");  
    writefileptr = fopen(WRITEFILENAME, "wb");

    fread(&wavfile_header_t, sizeof(wavfile_header_t), 1, readfileptr);
    wavfile_header_t.Subchunk2Size=786000;
    fwrite(&wavfile_header_t, sizeof(wavfile_header_t), 1, writefileptr);

    while((fread(&ADC_Value, 1, 2, readfileptr))>0) {
        Adjusted_ADC_Value=ADC_Value-32767;
        fwrite(&Adjusted_ADC_Value, 1, 2, writefileptr);
    };

    // Close the file
    fclose(readfileptr);
    fclose(writefileptr);

}

int write_wav_header(int SampleRate,int FrameCount)
{
    int ret=0;

    struct wavfile_header_s wav_header;
    int subchunk2_size;
    int chunk_size;

//    size_t write_count;

    // uint32_t bytes_written=0;

    // FRESULT result; /* FatFs function common result code */

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

	// //Open file for writing (Create)
	// 	result = f_write(&SDFile, &wav_header, sizeof(wavfile_header_t), (void *)&bytes_written);
	// 	if((bytes_written == 0) || (result != FR_OK))
	// 	{
	// 		Error_Handler();
	// 	}

	// // Flush the file buffers
	// 	result = f_sync(&SDFile);
	// 	if(result != FR_OK)
	// 	{
	// 		Error_Handler();
	// 	}
	return 1;
}