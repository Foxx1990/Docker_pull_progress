#!/bin/bash
# Ustawienia
IMAGE_NAME="ubuntu"
IMAGE_TAG="24.10"
JSON_FILE_PATH="docker_pull_status.json"

# Funkcja do pobierania obrazu
pull_image() {
    local url="http://localhost:5555/images/create?fromImage=${IMAGE_NAME}&tag=${IMAGE_TAG}"
    local total_bytes=0
    local total_progress=0
echo 'Pobieranie obrazu';
    # Wykonaj żądanie POST i odbierz odpowiedź
    curl -X POST "$url" | while IFS= read -r line; do
        if [[ -n "$line" ]]; then 
            local current=$(echo "$line" | jq '.progressDetail.current // 0') 
            local total=$(echo "$line" | jq '.progressDetail.total // 0') 
            total_bytes=$((total_bytes + total)) # Dodaj do łącznej ilości bajtów
            total_progress=$((total_progress + current))  # Dodaj do łącznej postępu

            if [[ $total_bytes -gt 0 ]]; then
                local percentage=$(echo "scale=4; ($total_progress / $total_bytes) * 100" | bc) # Oblicz procent
                local speed=$(echo "scale=2; $total_progress / ($SECONDS + 1)" | bc) # Avoid division by zero
                local remaining_time=$(echo "scale=0; ($total_bytes - $total_progress) / ($speed + 0.1)" | bc) # Avoid division by zero

                # Zapisz dane do pliku JSON
                echo $(jq -n --arg current_bytes "$total_progress" \
                              --arg total_bytes "$total_bytes" \
                              --arg percentage "$percentage" \
                              --arg speed "$speed" \
                              --arg remaining_time "$remaining_time" \
                              '{current_bytes: $current_bytes | tonumber, total_bytes: $total_bytes | tonumber, percentage: $percentage | tonumber, speed: $speed | tonumber, remaining_time: $remaining_time | tonumber}') > "$JSON_FILE_PATH"
            fi
        fi
    done
}

# Rozpocznij pobieranie obrazu
pull_image