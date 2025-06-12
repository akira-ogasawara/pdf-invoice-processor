#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF請求書自動処理スクリプト
- PDF解析（請求日、取引先、金額の抽出）
- ファイルリネーム (YYYYMMDD-{company}-{amount}.pdf)
- 印刷確認ダイアログ
- 両面モノクロ印刷
- 指定フォルダへの移動

GitHub: https://github.com/[YOUR_USERNAME]/pdf-invoice-processor
"""

import sys
import os
import shutil
import re
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pdfplumber

# ========== 設定項目 ==========
# 移動先フォルダパス（環境に合わせて変更してください）
DEST_FOLDER = "/Users/[USERNAME]/Library/CloudStorage/GoogleDrive-[EMAIL]/SharedDrives/Accounting/Invoices/FY2025/"

# 取引先名変換ルール（必要に応じて追加・変更してください）
COMPANY_MAPPING = {
    "Amazon": "amazon",
    "アマゾン": "amazon",
    "アマゾンジャパン": "amazon",
    "ダイワボウ情報システム": "daiwabo",
    "ヨドバシカメラ": "yodobashi",
    "楽天": "rakuten",
    "サンテレホン": "suntel",
    # 新しい取引先を追加する場合はここに記述
    # "取引先名": "short_name",
}

# MF会計手動登録が必要な会社（必要に応じて変更してください）
MANUAL_ACCOUNTING = ["daiwabo"]

def extract_invoice_data(pdf_path):
    """PDFから請求書データを抽出
    
    Args:
        pdf_path (str): PDFファイルのパス
        
    Returns:
        dict: 抽出されたデータ（date, company, amount, original_text）
        None: 抽出に失敗した場合
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        # 請求日の抽出（複数パターン対応）
        date_patterns = [
            r'請求書発行日[\s:：]*(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'請求日[\s:：]*(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        invoice_date = None
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.groups()
                invoice_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
                break
        
        if not invoice_date:
            # デフォルトで今日の日付を使用
            invoice_date = datetime.now().strftime("%Y%m%d")
            print(f"請求日が見つからないため、今日の日付 {invoice_date} を使用します")
        
        # 取引先の抽出
        company = "unknown"
        for company_name, short_name in COMPANY_MAPPING.items():
            if company_name in text:
                company = short_name
                break
        
        # 金額の抽出（複数パターン対応）- 総額（税込）を優先
        amount_patterns = [
            r'今回請求金額[（\(]税込[）\)][\s:：]*([0-9,]+)',
            r'請求金額[（\(]税込[）\)][\s:：]*([0-9,]+)',
            r'今回請求金額[\s:：]*([0-9,]+)',
            r'請求金額[\s:：]*([0-9,]+)',
            r'合計[\s:：]*[￥¥]?([0-9,]+)',  # Amazon形式対応
            r'売上金額[\s:：]*([0-9,]+)[\s]*円',
            r'[￥¥]([0-9,]+)(?=\s*$)',  # 行末の金額
            r'(\d{1,3}(?:,\d{3})*)[\s]*円'
        ]
        
        amount = "0"
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 最大の金額を採用（請求金額が複数ある場合）
                amounts = [int(m.replace(',', '')) for m in matches]
                amount = str(max(amounts))
                break
        
        return {
            'date': invoice_date,
            'company': company,
            'amount': amount,
            'original_text': text[:500]  # デバッグ用（最初の500文字）
        }
        
    except Exception as e:
        print(f"PDF解析エラー: {e}")
        return None

def show_print_dialog(filename, company, amount):
    """印刷確認ダイアログを表示
    
    Args:
        filename (str): ファイル名
        company (str): 取引先
        amount (str): 金額
        
    Returns:
        bool: 印刷するかどうか
    """
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    message = f"請求書を印刷しますか？\n\nファイル名: {filename}\n取引先: {company}\n金額: {amount}円"
    result = messagebox.askyesno("印刷確認", message)
    
    root.destroy()
    return result

def print_pdf(pdf_path):
    """PDFを両面モノクロで印刷
    
    Args:
        pdf_path (str): PDFファイルのパス
        
    Returns:
        bool: 印刷成功かどうか
    """
    try:
        cmd = [
            "lpr",
            "-o", "sides=two-sided-long-edge",  # 両面印刷（長辺綴じ）
            "-o", "ColorModel=Gray",            # モノクロ印刷
            pdf_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"印刷エラー: {e}")
        return False

def show_completion_dialog(results):
    """処理完了ダイアログを表示
    
    Args:
        results (list): 処理結果のリスト
    """
    root = tk.Tk()
    root.withdraw()
    
    message = "処理が完了しました。\n\n"
    for result in results:
        message += f"• {result['original_name']} → {result['new_name']}\n"
    
    # MF会計手動登録の注意喚起
    manual_files = [r for r in results if r['company'] in MANUAL_ACCOUNTING]
    if manual_files:
        message += "\n⚠️ 以下のファイルはMF会計への手動登録が必要です:\n"
        for result in manual_files:
            message += f"• {result['new_name']}\n"
    
    messagebox.showinfo("処理完了", message)
    root.destroy()

def process_invoice(pdf_path):
    """請求書処理のメイン関数
    
    Args:
        pdf_path (str): PDFファイルのパス
        
    Returns:
        dict: 処理結果
        None: 処理に失敗した場合
    """
    print(f"処理中: {pdf_path}")
    
    # PDF解析
    data = extract_invoice_data(pdf_path)
    if not data:
        print(f"PDF解析に失敗しました: {pdf_path}")
        return None
    
    # 新しいファイル名生成
    new_filename = f"{data['date']}-{data['company']}-{data['amount']}.pdf"
    print(f"新しいファイル名: {new_filename}")
    
    # 印刷確認
    if show_print_dialog(new_filename, data['company'], data['amount']):
        if print_pdf(pdf_path):
            print(f"印刷完了: {new_filename}")
        else:
            print(f"印刷に失敗しました: {new_filename}")
    
    # ファイル移動
    try:
        # 移動先フォルダが存在するか確認
        if not os.path.exists(DEST_FOLDER):
            print(f"エラー: 移動先フォルダが見つかりません: {DEST_FOLDER}")
            print("DEST_FOLDER の設定を確認してください")
            return None
        
        dest_path = os.path.join(DEST_FOLDER, new_filename)
        
        # 同名ファイルが存在する場合は連番を追加
        counter = 1
        base_name, ext = os.path.splitext(new_filename)
        while os.path.exists(dest_path):
            new_filename = f"{base_name}_{counter}{ext}"
            dest_path = os.path.join(DEST_FOLDER, new_filename)
            counter += 1
        
        shutil.move(pdf_path, dest_path)
        print(f"ファイル移動完了: {dest_path}")
        
        return {
            'original_name': os.path.basename(pdf_path),
            'new_name': new_filename,
            'company': data['company'],
            'dest_path': dest_path
        }
        
    except Exception as e:
        print(f"ファイル移動エラー: {e}")
        return None

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python invoice_processor.py <PDFファイル1> [PDFファイル2] ...")
        print("\n設定の確認:")
        print(f"移動先フォルダ: {DEST_FOLDER}")
        print(f"対応取引先: {list(COMPANY_MAPPING.keys())}")
        sys.exit(1)
    
    pdf_files = sys.argv[1:]
    results = []
    
    print(f"処理対象ファイル数: {len(pdf_files)}")
    print(f"移動先フォルダ: {DEST_FOLDER}")
    
    # 各PDFファイルを処理
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"ファイルが見つかりません: {pdf_file}")
            continue
        
        if not pdf_file.lower().endswith('.pdf'):
            print(f"PDFファイルではありません: {pdf_file}")
            continue
        
        result = process_invoice(pdf_file)
        if result:
            results.append(result)
    
    # 処理結果表示
    if results:
        show_completion_dialog(results)
        print(f"\n処理完了: {len(results)}ファイル")
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("エラー", "処理できるファイルがありませんでした。\n\n設定やファイル形式を確認してください。")
        root.destroy()
        print("処理できるファイルがありませんでした")

if __name__ == "__main__":
    main()
