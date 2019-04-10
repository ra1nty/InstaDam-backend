pydoc -w manage
pydoc -w wsgi

pydoc -w instadam
pydoc -w instadam.models
pydoc -w instadam.utils

instadam_files=$(find instadam -name "*.py")
for file in $instadam_files;
do
	file=${file//\//.}
	file=${file%.py}
	pydoc -w $file
done
