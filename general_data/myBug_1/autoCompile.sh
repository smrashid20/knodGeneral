#!/bin/bash

rm -rf out/
rm -rf lib/

mkdir -p lib/
wget -P lib/ https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar
wget -P lib/ https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar

mkdir -p out
javac -cp .:lib/* -d out $(find src test -name "*.java")
