#!/bin/bash

# Array of invoice files in chronological order
invoice_files=(
  "Invoice_1995-2019.csv"
  "Invoice_2020.csv"
  "Invoice_2021.csv"
  "Invoice_2022.csv"
  "Invoice_2023.csv"
  "Invoice_2024.csv"
  "Invoice_2025.csv"
)

downloads_path="/Users/kebsi/Downloads"
total_files=${#invoice_files[@]}

echo "🚀 Starting sequential processing of $total_files invoice files..."
echo "⏳ Each file will complete both steps before moving to the next"
echo ""

for i in "${!invoice_files[@]}"; do
  file="${invoice_files[$i]}"
  file_number=$((i + 1))
  
  echo "📂 [$file_number/$total_files] Processing: $file"
  echo "================================"
  
  file_path="$downloads_path/$file"
  
  if [ ! -f "$file_path" ]; then
    echo "❌ File not found: $file_path"
    continue
  fi
  
  echo "📥 Step 1: Reading file to database..."
  start_time=$(date +%s)
  
  if node read-file-2-db.js "$file_path" qlik_invoice_raw; then
    read_time=$(($(date +%s) - start_time))
    echo "✅ File read completed in ${read_time}s"
    
    echo "⚡ Step 2: Executing delta operations..."
    delta_start_time=$(date +%s)
    
    if node execute_qlik_delta.js; then
      delta_time=$(($(date +%s) - delta_start_time))
      total_time=$(($(date +%s) - start_time))
      echo "✅ Delta operations completed in ${delta_time}s"
      echo "🎯 Total time for $file: ${total_time}s"
    else
      echo "❌ Delta operations failed for $file"
      echo "🛑 Stopping execution due to delta failure"
      exit 1
    fi
  else
    echo "❌ Failed to read file: $file"
    echo "🛑 Stopping execution due to read failure"
    exit 1
  fi
  
  echo ""
  if [ $file_number -lt $total_files ]; then
    echo "⏭️  Moving to next file..."
    echo ""
  fi
done

echo "🎉 All $total_files invoice files processed successfully!"