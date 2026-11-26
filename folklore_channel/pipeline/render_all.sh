set -e
cd "$(dirname "$0")/.."; mkdir -p renders
declare -A NAME=([1]="Krampus" [2]="the Wendigo" [3]="Baba Yaga" [4]="the Wild Hunt")
declare -A TID=([1]=k07 [2]=w06 [3]=b07 [4]=h06)
for n in 1 2 3 4; do
  python3 pipeline/film.py render episodes/ep0$n/ep0$n.film renders/EP0$n.mp4 > renders/ep0$n.log 2>&1
  python3 pipeline/upload_kit.py ep0$n renders/EP0$n.times.json
  python3 pipeline/short.py renders/EP0$n.mp4 "${NAME[$n]}" renders/EP0${n}_short.mp4 ${TID[$n]}
  echo "done $n"
done
