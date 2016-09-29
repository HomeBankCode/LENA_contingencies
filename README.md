# LENA_contingencies
GUI for computing contingency tables from .its files.

## HOW TO RUN THIS SOFTWARE

### (1) Set up a configuration file for batch analysis

> A configuration file is used to define the batch of .its files to be analyzed. The configuration files is a .csv file where the first column specifies a subject ID and subsequent columns specify paths to .its files associated with that subject. See the example configuration below:

| id | file1 | . . . | fileN |
|-------|----|-------|--------|
| 101|  C:/example1.its  | . . . | C:/exampleN.its      |
|⋮|⋮|⋮|⋮|
| 237| C:/anotherexample1.its | . . . | C:/anotherexampleN.its |

> Note: You must specify the *full* path to the file and you must include the file extension (.its). Please use forward slashes in paths. If the path is not specified correctly, the program will not analyze the file.

### (2) Run the program from the source code

> The entry point of the program is in the file control.py. To run the program, enter the following command line instruction:

<code>>>> python /.../path/to/direcotry/control.py</code>
> Once the program launces, you can begin specifying the details of the anlaysis to be conducted. The video below gives a walkthrough on using the interface:

[![Video Demo](http://research.vuse.vanderbilt.edu/rasl/wp-content/uploads/2016/09/LENA_contingencies%20Video%20Demo%20Img.jpg)](https://www.youtube.com/watch?v=LG-wz6yGV6g&feature=youtu.be)
