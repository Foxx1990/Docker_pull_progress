#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 23.11.2024 Marcin Polonis
# All rights reserved.
#
# Skrypt do monitorowania pobierania obrazów Dockera i zapisywania statusu w pliku JSON.

import json
import requests
import time
import os

IMAGE_NAME = 'ubuntu/jre'
IMAGE_TAG = '8-22.04_edge'
JSON_FILE_PATH = 'docker_pull_status.json'

def pull_image(image_name, image_tag):
    url = f"http://localhost:5555/images/create?fromImage={image_name}&tag={image_tag}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, stream=True)

    return response

def monitor_pull(response):
    total_bytes = 0
    total_progress = 0
    start_time = time.time()
    last_bytes = 0

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if 'progressDetail' in data:
                current = data['progressDetail'].get('current', 0)
                total = data['progressDetail'].get('total', 0)

                if total > 0:
                    # Zaktualizuj całkowity postęp
                    total_bytes += total
                    total_progress += current
                    
                    percentage = (total_progress / total_bytes) * 100 if total_bytes > 0 else 0
                    speed = (total_progress - last_bytes) / (time.time() - start_time) if start_time != time.time() else 0
                    remaining_time = (total_bytes - total_progress) / speed if speed > 0 else 0

                    last_bytes = total_progress
                    start_time = time.time()

                    status_data = {
                        'current_bytes': total_progress,
                        'total_bytes': total_bytes,
                        'percentage': round(percentage, 2),
                        'speed': round(speed, 2),
                        'remaining_time': round(remaining_time)
                    }

                    # Zapisz dane do pliku JSON
                    with open(JSON_FILE_PATH, 'w') as json_file:
                        json.dump(status_data, json_file)

                    print(status_data)

if __name__ == "__main__":
    response = pull_image(IMAGE_NAME, IMAGE_TAG)
    monitor_pull(response)
