#!/bin/sh

if [ $# -lt 1 ]
 then 
 	echo "Please specify at least one scheme for your project: ./desploy.sh \"WhiteWall\" \"WhiteWall Beta\""
else
	echo "---- update build version ----"
	agvtool next-version -all

	for scheme in "$@"
	do
		echo "---- remove previous ipa and .dSYM ----"
		rm -rf ~/Desktop/"$scheme".app.dSYM.zip ~/Desktop/"$scheme".ipa

		echo "---- build .app file ----"
		xcodebuild -workspace *.xcworkspace -scheme "$scheme" -configuration "release" -derivedDataPath ~/Desktop

		cd ~/Desktop/Build/Products/Release-iphoneos/

		echo "---- create .ipa file ----"
		xcrun -sdk "iphoneos" PackageApplication -v *.app -o ~/Desktop/"$scheme".ipa

		echo "---- create .zip file ----"
		zip -r ~/Desktop/"$scheme".app.dSYM.zip *.dSYM

		echo "---- removing teporary files ----"
		rm -rf ~/Desktop/Build ~/Desktop/ModuleCache ~/Desktop/info.plist

		cd -
	done

	git add .
	git commit -m "Increment Build Number"

	open ~/Desktop

fi


