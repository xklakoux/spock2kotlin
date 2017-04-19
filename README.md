# spock2kotlin 

best effort parser from spock to kotlin

spock2kotlin uses python3

### Usage
usage `python3 parsespocky.py [path]`

where `path` could be 
* path to test/groovy, then it parses groovy files recursively and creates kotlin files in test/kotlin/
* path to YourSpockTest.groovy file, then it parses file and outputs YourSpockTestKt.kt, but if the file resides in test/groovy directory then it outputs new file in test/java
