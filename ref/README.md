# Yay0 Decompressor

This is a slightly adapted version of the decoder implementation for Yay0 available from https://github.com/pho/WindViewer/wiki/Yaz0-and-Yay0. Below are the changes done to fix bugs/ improve performance.

Changes after inital version:
1. `r5` used twice with diff types. Change `r5` to `r51` in block copy case where it's used as `void*`;
2. Add declaration for missing variables:
        u32 r21, r29, r23, r31, r28, r24, r22, r25 ;
        u16 r26, r30 ;
        u8 r5;
        void *r51;
3. Modified `Decode` function to return pointer to the decoded data as well as allocate memory for it insideof itself.
4. add b2l_* helper functions to make it work on little-endian systems.
5. Abuse of `i` for decoded size as well as loop index for block copy led to a bug. Introduced `ind` for loop-index.
