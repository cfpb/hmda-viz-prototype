# execute from root directory of repo with "./2017-json-formats/scripts/remove-whitespace.sh"

for name in $(ls 2017-json-formats/aggregate)
do
  sed -i '' "s/[ \t]*$//" "2017-json-formats/aggregate/$name"
done

for name in $(ls 2017-json-formats/disclosure)
do
  sed -i '' "s/[ \t]*$//" "2017-json-formats/disclosure/$name"
done
