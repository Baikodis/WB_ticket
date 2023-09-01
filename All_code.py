import os
import io
import fitz
from PIL import Image, ImageDraw, ImageFont
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

range_name = ["'Для печати'!A5:A", "'Для печати'!G5:G"]


def alg(spreadsheet_id, pdf_file, pdf_name):
    name_file = f'edit_{pdf_name}'

    # Блок проверки данных для подключения к Google Sheets
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expiry and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Основной блок считывания данных с таблицы
    try:

        # Подключение к таблице
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=range_name,
        ).execute()

        # Получение информации с таблицы
        values = result.get('valueRanges', [])
        labels = values[1].get('values', [])
        p_p = values[0].get('values', [])
        if not values:
            print('No data found')
            return ""

        # Блок с созданием и наполнением словаря для поиска по ключу "этикетка"
        my_dict = {}
        i = 0
        for row in labels:
            my_dict[row[0]] = p_p[i][0]
            i += 1

        # Блок редактирования pdf файла
        with fitz.open(pdf_file) as doc:

            # Цикл по каждой отдельной странице
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = " / ".join(page.get_text().split('\n')[:-1])
                try:
                    numbers = my_dict[text]
                except Exception as ex:
                    continue

                # Эти ухищрения нужны для сохранения качества qr кода
                pix = page.get_pixmap(alpha=True)
                img_bytes = pix.tobytes()
                img_data = io.BytesIO(img_bytes)
                img = Image.open(img_data).convert("RGB")
                alpha = Image.new('L', img.size, 0)
                img.putalpha(alpha)

                img = img.rotate(270, expand=True)
                width, height = img.size
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype('arial.ttf', 14)
                text_width, text_height = draw.textsize(numbers, font=font)

                x = 0
                y = height - text_height - 5
                draw.text((x, y), numbers, font=font, fill=(0, 0, 0, 255))
                img = img.rotate(-270, expand=True)

                temp_file = "image.png"
                img.save(temp_file, format="PNG")
                new_image = fitz.Pixmap(temp_file)
                page.insert_image(page.rect, pixmap=new_image)
                os.remove(temp_file)

            doc.save(f'temp/{name_file}')
        return f'temp/{name_file}'

    except HttpError as err:
        print(f'An error occurred: {err}')
        return ""


if __name__ == "__main__":
    pdf_file = 'temp/стикеры.pdf'
    spreadsheet_id = "1pgCuZb0PkXHUASb4u0xGp27zJnLO0zli50aK8R6kDc8"
    alg(spreadsheet_id, pdf_file)
