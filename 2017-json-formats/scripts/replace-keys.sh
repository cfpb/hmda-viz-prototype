# execute from repo root: "./2017-json-formats/scripts/replace-keys.sh"

for name in $(ls 2017-json-formats/aggregate)
do
  sed -i '' -f 2017-json-formats/scripts/keys-corrections "2017-json-formats/aggregate/$name"
done

for name in $(ls 2017-json-formats/disclosure)
do
  sed -i '' -f 2017-json-formats/scripts/keys-corrections "2017-json-formats/disclosure/$name"
done
