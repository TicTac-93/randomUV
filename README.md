# randomUV
A 3dsMax script that works with the UnwrapUVW modifier to randomize UV element transforms.

Install by copying the randomUV folder to your 3ds Max scripts directory.
Run in 3ds Max using with the MaxScript snippet:
`python.ExecuteFile @"C:\path\to\randomUV\randomUV.py"`

-----

This script makes use of the `Unwrap UVW` modifier to randomize UV island transforms, rotations, and scales.

To use, run the script and select some UV islands in an `Unwrap UVW` modifier.  You can select sub-elements
(they will be expanded to full islands by the script), including individual vertices or edges.

With some UV elements selected, press the `1 - Hold UV Selection` button.
Depending on the number of elements selected, this may take some time.

Next, check which transforms you'd like to randomize and set the min/max amounts.
Units for these are UV space for Translation, degrees for Rotation, and Percent for Scale.
Optionally, you can also set Increment values for each transform.

With Channels selected and Min/Max/Increment values set, you can press `2 - Randomize UVs` to... randomize your UVs.
This ***is*** undo-able.

-----

Important notes:
- The `Unwrap UVW` modifier ***must*** be selected when you are Holding Selection
and Randomizing UVs.
- You need to have the same object selected when you Hold Selection and when you Randomize.
- You ***should*** have the same `Unwrap UVW` modifier selected when you Hold Selection
and when you Randomize UVs.  The script won't enforce this, but it will likely behave weirdly or
fail outright if you don't.