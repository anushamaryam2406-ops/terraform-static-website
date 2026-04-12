# क्लाउड पोर्टफोलियो वेबसाइट — AWS सर्वरलेस होस्टिंग

एक प्रोडक्शन-ग्रेड पोर्टफोलियो वेबसाइट जो पूरी तरह AWS पर सर्वरलेस आर्किटेक्चर और इंफ्रास्ट्रक्चर एज कोड का उपयोग करके होस्ट की गई है। CloudFront के माध्यम से ग्लोबल CDN डिलीवरी और एक रीयल-टाइम विजिटर काउंटर की सुविधा है।

---

## लाइव साइट

लाइव साइट: https://d200wx852sfwd7.cloudfront.net

API एंडपॉइंट: https://9ocjb0c947.execute-api.eu-north-1.amazonaws.com/prod/visit

---

## यह प्रोजेक्ट क्या करता है

एक स्टैटिक पोर्टफोलियो वेबसाइट जो S3 पर होस्ट की गई है और CloudFront CDN के माध्यम से डिलीवर की जाती है। हर पेज विजिट एक सर्वरलेस विजिटर काउंटर को ट्रिगर करता है जो गिनती को DynamoDB में स्टोर करता है और पेज पर लाइव दिखाता है।

```
यूजर साइट विजिट करता है
      |
      v
CloudFront CDN     <- HTML/CSS को ग्लोबली सर्व करता है
      |
      v
S3 बकेट          <- index.html, style.css स्टोर करता है (प्राइवेट)

अलग से:
पेज लोड होता है -> JS विजिटर काउंट फेच करता है
      |
      v
API Gateway -> Lambda -> DynamoDB (गिनती बढ़ाता है)
      |
      v
काउंट रीयल टाइम में पेज पर दिखाया जाता है
```

---

## आर्किटेक्चर

| लेयर | सेवा | उद्देश्य |
|---|---|---|
| CDN | CloudFront | ग्लोबल डिलीवरी, HTTPS, कैशिंग |
| स्टोरेज | S3 | स्टैटिक फाइल होस्टिंग (प्राइवेट बकेट) |
| सुरक्षा | Origin Access Control (OAC) | केवल CloudFront ही S3 को पढ़ सकता है |
| API | API Gateway | विजिटर काउंटर के लिए REST एंडपॉइंट |
| कंप्यूट | Lambda (Python 3.11) | विजिटर काउंट को एटॉमिकली बढ़ाता है |
| डेटाबेस | DynamoDB | विजिटर काउंट स्टोर करता है (PAY_PER_REQUEST) |
| IaC | Terraform | सभी इंफ्रास्ट्रक्चर कोड के रूप में |
| स्टेट | S3 रिमोट बैकएंड | टीम-सेफ Terraform स्टेट |

![आर्किटेक्चर](architecture.png)

---

## मुख्य डिज़ाइन निर्णय

**प्राइवेट S3 बकेट OAC के साथ (पब्लिक नहीं)**
S3 बकेट के पास कोई पब्लिक एक्सेस नहीं है। केवल CloudFront Origin Access Control के माध्यम से फाइलें पढ़ सकता है। यह आधुनिक AWS अप्रोच है — पुराना Origin Access Identity (OAI) को डिप्रिकेट किया गया है।

> "मैंने OAC का उपयोग किया क्योंकि OAI को डिप्रिकेट किया गया है और OAC अधिक S3 फीचर्स को सपोर्ट करता है जिसमें SSE-KMS एन्क्रिप्शन भी शामिल है।"

**ग्लोबल डिलीवरी के लिए CloudFront**
CloudFront के बिना, eu-north-1 से दूर के यूजर्स को उच्च लेटेंसी का सामना करना पड़ेगा। CloudFront दुनिया भर के एज लोकेशन्स पर कंटेंट को कैश करता है — यूजर्स को निकटतम एज से साइट मिलता है, न कि स्टॉकहोम से।

**DynamoDB एटॉमिक इनक्रीमेंट**
Lambda UpdateExpression में `ADD` का उपयोग करता है — यह एक एटॉमिक ऑपरेशन है। भले ही 1000 यूजर एक साथ विजिट करें, हर इनक्रीमेंट को सही तरीके से गिना जाता है रेस कंडीशन के बिना।

**PAY_PER_REQUEST बिलिंग**
पोर्टफोलियो साइट्स में अप्रत्याशित, कम ट्रैफिक होता है। PAY_PER_REQUEST का मतलब है कि जब कोई विजिट नहीं करता तो शून्य लागत। प्रोविजन्ड कैपेसिटी रिजर्व्ड कैपेसिटी के साथ पैसा बर्बाद करेगी जो निष्क्रिय बैठी होती।

---

## प्रोजेक्ट संरचना

```
static-website/
├── index.html              <- विजिटर काउंटर के साथ पोर्टफोलियो पेज
├── style.css               <- रेस्पॉन्सिव CSS, मोबाइल-फ्रेंडली
├── lambda_function.py      <- विजिटर काउंटर Lambda हैंडलर
├── main.tf                 <- S3 + CloudFront + OAC
├── api_gateway.tf          <- REST API एंडपॉइंट
├── lambda.tf               <- Lambda फंक्शन + IAM रोल
├── dynamodb.tf             <- विजिटर काउंट टेबल
└── .gitignore              <- स्टेट फाइल्स और zips को इग्नोर करता है
```

---

## विजिटर काउंटर कैसे काम करता है

```python
# Lambda DynamoDB ADD का उपयोग करके काउंट को एटॉमिकली इनक्रीमेंट करता है
response = table.update_item(
    Key={"id": "main"},
    UpdateExpression="ADD visit_count :inc",
    ExpressionAttributeValues={":inc": 1},
    ReturnValues="UPDATED_NEW"
)
```

DynamoDB में `ADD` ऑपरेशन एटॉमिक है — यह एक ऑपरेशन में पढ़ता और इनक्रीमेंट करता है, उच्च कॉनकरेंसी के तहत भी रेस कंडीशन को रोकता है।

फ्रंटएंड पेज लोड पर इस काउंट को फेच करता है:

```javascript
const res = await fetch(API_URL);
const data = await res.json();
document.getElementById("visitCount").textContent = data.visits;
```

---

## सेटअप और डिप्लॉयमेंट

**पूर्वापेक्षाएं:** AWS CLI कॉन्फ़िगर किया गया, Terraform >= 1.0, Python 3.11

**1. Lambda को पैकेज करें:**
```bash
zip lambda.zip lambda_function.py
```

**2. इंफ्रास्ट्रक्चर डिप्लॉय करें:**
```bash
terraform init
terraform plan
terraform apply
```

**3. अपने URLs प्राप्त करें:**
```bash
terraform output cloudfront_url
terraform output api_url
```

**4. अपनी साइट विजिट करें:**
```
https://{d200wx852sfwd7.cloudfront.net}
```

पहली बार डिप्लॉ��� पर CloudFront को ~5 मिनट लगते हैं प्रोपेगेट करने में।

---

## आउटपुट्स

`terraform apply` के बाद:

```
cloudfront_url = "https://{d200wx852sfwd7.cloudfront.net}"
api_url        = "https://{9ocjb0c947.execute-api.eu-north-1.amazonaws.com/prod/visit}."
```

---

## क्लीनअप

```bash
terraform destroy
```

सभी AWS रिसोर्सेस को हटाता है — S3, CloudFront, Lambda, API Gateway, DynamoDB, IAM रोल्स।

---

## समस्या निवारण

**विजिटर काउंटर "Error" दिखाता है:**
```bash
aws logs tail /aws/lambda/visitor-counter --follow
```
जांचें कि Lambda के पास DynamoDB परमिशन हैं और टेबल मौजूद है।

**CloudFront 403 दिखाता है:**
डिप्लॉय के बाद कैश प्रोपेगेशन के लिए 5 मिनट प्रतीक्षा करें। सत्यापित करें कि S3 बकेट पॉलिसी CloudFront OAC को सही तरीके से संदर्भित करती है।

**Terraform स्टेट लॉक:**
```bash
terraform force-unlock {lock-id}
```

---

## तकनीकें

| घटक | तकनीक |
|---|---|
| फ्रंटएंड | HTML5, CSS3 |
| होस्टिंग | AWS S3 + CloudFront |
| बैकएंड | AWS Lambda (Python 3.11) |
| API | AWS API Gateway (REST) |
| डेटाबेस | AWS DynamoDB |
| IaC | Terraform |
| रीजन | eu-north-1 (स्टॉकहोम) |

---

## लेखक

**अनुषा मरियम** — AWS क्लाउड इंजीनियर
GitHub: [@anushamaryam2406-ops](https://github.com/anushamaryam2406-ops)