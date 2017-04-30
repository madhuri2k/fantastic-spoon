/*
  Reference implementation for yay0 decoder from 
  https://github.com/pho/WindViewer/wiki/Yaz0-and-Yay0

  Changes after inital version:
  1. r5 used twice with diff types. Change r5 to r51 in block copy case where 
        it's used as void*;
  2. Add declaration for missing variables: 
        u32 r21, r29, r23, r31, r28, r24, r22, r25 ;
        u16 r26, r30 ;
        u8 r5;
        void *r51;
  3. Modified function to return decoded data pointer and allocate memory for 
        it inside the func
        void *d;
  4. add b2l_* helper functions to make it work on little-endian system
  5. abuse of i for decoded size as well as loop index for block copy. introduced ind 
        for loop-index.

*/

#include <stdio.h>
#include <stdlib.h>

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

// Convert a 32-bit number from big to little endian and back
u32 b2l_u32(u32 num) {
    u32 swapped = ((num>>24)&0xff) | // move byte 3 to byte 0
                    ((num<<8)&0xff0000) | // move byte 1 to byte 2
                    ((num>>8)&0xff00) | // move byte 2 to byte 1
                    ((num<<24)&0xff000000); // byte 0 to byte 3
    return swapped ;
}

// Convert a 16-bit number from big to little endian and back
u16 b2l_u16(u16 num) {
    u16 swapped = ((num>>8) & 0xff) | ((num<<8) & 0xff00);
    return swapped ;
}


void *Decode(void* s)
{
    u32 i, j, k;
    u32 p, q;
    u32 cnt;
    u32 r21, r29, r23, r31, r28, r24, r22, r25, instr = 0 ;
    u16 r26, r30 ;
    u8 r5;
    void *r51;
    void *d;
    u8* cs = (u8*) s ;
    i = r21 = b2l_u32(*((u32*) (s + 4))); // size of decoded data 
    j = r29 = b2l_u32(*(u32*) (s + 8)); // link table 
    k = r23 = b2l_u32(*(u32*) (s + 12)); // byte chunks and count modifiers 
    q = r31 = 0; // current offset in dest buffer 
    cnt = r28 = 0; // mask bit counter 
    p = r24 = 16; // current offset in mask table 

    // Try to allocate memory for destination
    d = (void *) malloc(i);
    if(d == (void *) NULL) {
        printf("Unable to allocate memory!");
        return NULL ;
    }
    printf("Preamble: ");
    for (int index = 0; index < 8; index++) {
        printf(" [%x] ", cs[index]);
    }
    printf("\nstart %p sizept %p Dec size %u, offsets: m %u, dc %u.\n", s, s+4, i, j, k);
    do
    {
        // if all bits are done, get next mask 
        if (cnt == 0)
        {
            printf("Mask offset %u...", p);
            // read word from mask data block 
            r22 = b2l_u32(*(u32*) (s + p));
            p += 4;
            cnt = 32; // bit counter 
            printf("Moved to %u.\n", p);
        }
        // if next bit is set, chunk is non-linked 
        if (r22 & 0x80000000)
        {
            // get next byte 
            *(u8*) (d + q) = *(u8*) (s + k);
            k++;
            q++;
        } 
            // do copy, otherwise 
        else
        {
            // read 16-bit from link table 
            r26 = b2l_u16(*(u16*) (s + j));
            j += 2;
            // 'offset' 
            r25 = q - (r26 & 0xfff);
            // 'count' 
            r30 = r26 >>  12;
            if (r30 == 0)
            {
                // get 'count' modifier 
                r5 = *(u8*) (s + k);
                k++;
                r30 = r5 + 18;
            }
            else r30 += 2;
            // do block copy 
            r51 = d + r25;
            instr++ ;
            if(instr == 1) {
                printf("Linked chunk: dist %u, o_dest %u, offset %u\n", 
                    (r26 & 0xfff), q, r25);
                printf("Moved %p to %p but copying from %p (%x bytes) to %p.\n", 
                    d, r51, r51-1, r30, r51-1+r30);
                printf("File offsets: %x to %x.\n", q, q+r30) ;
            }
            for (u32 ind = 0; ind < r30; ind++)
            {
                *(u8*) (d + q) = *(u8*) (r51 - 1);
                q++;
                r51++;
            }
        }
        // next bit in mask 
        r22 <<=  1;
        cnt--;
    } while (q < i);

    printf("Wrote %u bytes.\n", q);

    return d ;
}


void * getData(char *filename) {
    unsigned char *s ;
    FILE *fp ;
    size_t size, asize ;

    fp = fopen(filename, "rb") ;
    if(fp != (FILE *)NULL) {
        fseek(fp, 0, SEEK_END) ;
        size = ftell(fp) ;
        printf("Size is %lu.\n", size);
        fseek(fp, 0, SEEK_SET) ;
        s = (unsigned char *) malloc(size) ;
        if(s != (unsigned char *) NULL) {
            asize = fread(s, 1, size, fp) ;
            if(asize != size) {
                printf("error: Expecting %lu bytes. Read %lu bytes.\n", size, asize) ;
            }
            fclose(fp) ;
            return (void *) s;
        } else {
            printf("error: Unable to allocate buffer of %lu bytes.\n", size) ;
            fclose(fp) ;
            return NULL ;
        }
    } else {
        printf("error: Unable to open file [%s].\n", filename);
        return  NULL ;
    }
}


int putData(char *filename, size_t size, void *buffer) {
    FILE *fp;
    size_t asize ;
    if( (fp=fopen(filename,"wb")) != (FILE *) NULL) {
        asize = fwrite(buffer, 1, size, fp) ;
        fclose(fp);
        printf("Successfully wrote %lu bytes.\n", asize);
    } else {
        printf("error: Unable to open: %s.\n", filename);
    }
    return 0;
}

int main() {

    void *s, *d ;
    size_t unc_size ;

    printf("Size of int: %lu, long: %lu, short: %lu, char: %lu\n", 
        sizeof(int), sizeof(long), sizeof(short), sizeof(char));

    s = getData("game_over.256x32.ci8") ;
    unc_size = b2l_u32(*((u32*) (s + 4))); // size of decoded data 
    printf("Retrieved data %p of uncompressed size %lu bytes.\n", s, unc_size);
    d = Decode(s) ;
    printf("Decoded into %lu bytes\n", sizeof(d));
    return putData(
        "game_over.256x32.raw",
        unc_size,
        d);
}
