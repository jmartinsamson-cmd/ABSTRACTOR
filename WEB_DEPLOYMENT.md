# 🌐 ABSTRACTOR Web Deployment Guide

**Deploy your PDF Form Processor to the web - access from anywhere!**

---

## 🎯 Quick Deployment (Streamlit Cloud - FREE)

### Step 1: Your GitHub Repo is Ready ✅

You already have:

- ✅ Repository: `jmartinsamson-cmd/ABSTRACTOR`
- ✅ All code committed and pushed
- ✅ Web app files created

### Step 2: Deploy to Streamlit Cloud (5 minutes)

1. **Go to Streamlit Cloud**
   - Visit: <https://share.streamlit.io/>
   - Click "Sign in with GitHub"
   - Authorize Streamlit to access your repositories

2. **Create New App**
   - Click "New app" button
   - Select your repository: `jmartinsamson-cmd/ABSTRACTOR`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

3. **Wait for Deployment** (2-3 minutes)
   - Streamlit will install dependencies from `requirements_web.txt`
   - Install system packages from `packages.txt` (Tesseract OCR)
   - Build and launch your app

4. **Get Your URL**
   - Your app will be live at: `https://[app-name].streamlit.app`
   - Share this URL with your wife - no installation needed!

---

## 📋 Files Created for Web Deployment

```
ABSTRACTOR/
├── streamlit_app.py          # Main web application ⭐ NEW
├── requirements_web.txt       # Web dependencies ⭐ NEW
├── packages.txt              # System packages (Tesseract) ⭐ NEW
├── .streamlit/
│   └── config.toml           # Streamlit configuration ⭐ NEW
└── templates/
    └── STEP2.pdf             # Form template (upload to GitHub)
```

---

## 🚀 How It Works

### User Experience (Your Wife)

1. **Open URL** - `https://your-app.streamlit.app`
2. **Upload PDFs** - Drag & drop source files
3. **Configure** - Enable OCR, set template path
4. **Click "Process PDFs"** - Watch live progress
5. **Download Results** - Get JSON data and filled forms

### Behind the Scenes

```
User uploads PDF → Streamlit processes in temp directory
                 → Extract text (PyPDF2)
                 → OCR if needed (Tesseract)
                 → Extract fields (patterns)
                 → Fill form template (PyMuPDF)
                 → Return filled PDF to browser
                 → User downloads completed form
```

---

## 🔧 Configuration

### Streamlit Cloud Settings

**File Upload Limit:** 200 MB (set in `.streamlit/config.toml`)

**Memory:** 1 GB free tier (sufficient for most PDFs)

**Timeout:** 10 minutes per request

### Template Path

Update in the app sidebar or modify default in `streamlit_app.py`:

```python
template_path = st.sidebar.text_input(
    "Form Template Path",
    value="templates/STEP2.pdf",  # Change this
    help="Path to the PDF form template"
)
```

---

## 📦 What Gets Installed

### Python Packages (`requirements_web.txt`)

```
streamlit>=1.28.0         # Web framework
PyPDF2==3.0.1            # PDF reading
PyMuPDF>=1.23.0          # PDF form filling
pytesseract==0.3.10      # OCR interface
pdf2image==1.16.3        # PDF to image
Pillow>=10.0.0           # Image processing
```

### System Packages (`packages.txt`)

```
tesseract-ocr            # OCR engine
tesseract-ocr-eng        # English language data
poppler-utils            # PDF rendering
```

---

## 🎨 Customization

### Change App Title

Edit `streamlit_app.py`:

```python
st.set_page_config(
    page_title="Abstractor - PDF Form Processor",  # Change this
    page_icon="📄",  # Change emoji
    layout="wide",
)
```

### Change Color Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"      # Main accent color
backgroundColor = "#ffffff"    # Page background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar
textColor = "#262730"         # Text color
```

### Add Custom Logo

```python
st.image("path/to/logo.png", width=200)
st.markdown('<h1 class="main-title">📄 ABSTRACTOR</h1>')
```

---

## 🔐 Security & Privacy

### Data Handling

✅ **Temporary Processing** - Files deleted after processing  
✅ **No Data Storage** - Nothing saved on server  
✅ **Session Isolation** - Each user has separate session  
✅ **HTTPS** - Encrypted transmission (Streamlit Cloud default)

### Template File Security

**Important:** If your `STEP2.pdf` template contains sensitive data:

1. **Option A:** Don't commit it to GitHub
   - Add `templates/*.pdf` to `.gitignore`
   - Users upload their own template via the app

2. **Option B:** Create sanitized template
   - Remove any pre-filled sensitive data
   - Commit clean template to repository

3. **Option C:** Private Repository
   - Make GitHub repo private (Settings → Danger Zone)
   - Streamlit Cloud works with private repos

---

## 🌍 Alternative Hosting Options

### Option 2: Render (Free Tier)

1. **Create Render Account**: <https://render.com/>
2. **New Web Service** → Connect GitHub repo
3. **Build Command**: `pip install -r requirements_web.txt`
4. **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT`
5. **Add Environment Variables** (if needed)

### Option 3: Railway (Easy Deploy)

1. **Create Railway Account**: <https://railway.app/>
2. **New Project** → Deploy from GitHub
3. **Select ABSTRACTOR repository**
4. **Railway auto-detects Streamlit**
5. **Click Deploy**

### Option 4: Heroku (More Control)

Create `Procfile`:

```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:

```
python-3.11.6
```

Deploy:

```bash
heroku create abstractor-app
git push heroku main
```

---

## 🐛 Troubleshooting

### "Module not found" Error

**Solution:** Check `requirements_web.txt` includes all dependencies

```bash
# Test locally first
pip install -r requirements_web.txt
streamlit run streamlit_app.py
```

### OCR Not Working

**Solution:** Verify `packages.txt` is in root directory

```
tesseract-ocr
tesseract-ocr-eng
poppler-utils
```

### File Upload Fails

**Solution:** Increase upload limit in `.streamlit/config.toml`

```toml
[server]
maxUploadSize = 200  # MB
```

### Template Not Found

**Solution:** Ensure `templates/` folder is committed to GitHub

```bash
git add templates/STEP2.pdf
git commit -m "Add form template"
git push
```

Then restart Streamlit Cloud app.

### App Crashes During Processing

**Solutions:**

1. Reduce PDF size (split large files)
2. Disable OCR for simple text PDFs
3. Upgrade to Streamlit Cloud paid tier (more memory)

---

## 📊 Performance Tips

### Speed Optimization

1. **Cache Results** - Add Streamlit caching:

```python
@st.cache_data
def process_pdf(uploaded_file, use_ocr=True):
    # ... processing code
```

2. **Batch Processing** - Process files in parallel (advanced)

3. **Lazy OCR** - Only use OCR when text extraction fails

### Memory Management

- Close PDF handles after processing
- Clear session state when done
- Use temporary directories (auto-cleanup)

---

## 🔄 Updating Your Deployed App

### Push Changes to GitHub

```bash
# Make changes to streamlit_app.py
git add .
git commit -m "Update web app features"
git push
```

**Streamlit Cloud auto-detects changes and redeploys!**

### Manual Redeploy

If auto-deploy doesn't trigger:

1. Go to <https://share.streamlit.io/>
2. Find your app
3. Click "⋮" menu → "Reboot app"

---

## 📱 Mobile Access

The Streamlit app is **mobile-responsive**:

✅ Works on phones & tablets  
✅ Touch-friendly file upload  
✅ Responsive layout  
✅ Download results on mobile

Your wife can process PDFs from her phone!

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| **Streamlit Cloud** | ✅ Unlimited public apps | $20/mo for private |
| **Render** | ✅ 750 hours/mo | $7/mo (always-on) |
| **Railway** | ✅ $5 credit/mo | $5/mo minimum |
| **Heroku** | ❌ No free tier | $7/mo minimum |

**Recommendation:** Start with **Streamlit Cloud** (easiest + free)

---

## ✅ Deployment Checklist

Before deploying:

- [ ] All code committed to GitHub
- [ ] `streamlit_app.py` created
- [ ] `requirements_web.txt` created
- [ ] `packages.txt` created (for OCR)
- [ ] `.streamlit/config.toml` created
- [ ] `templates/STEP2.pdf` committed (or `.gitignore`d)
- [ ] Tested locally: `streamlit run streamlit_app.py`

After deploying:

- [ ] App loads without errors
- [ ] File upload works
- [ ] PDF processing completes
- [ ] Download buttons work
- [ ] OCR functions (if enabled)
- [ ] Form filling produces valid PDF
- [ ] Share URL with your wife

---

## 🎓 Next Steps

### 1. Local Testing

```bash
# Install web dependencies
pip install -r requirements_web.txt

# Run locally
streamlit run streamlit_app.py

# Opens browser at: http://localhost:8501
```

### 2. Push to GitHub

```bash
git add streamlit_app.py requirements_web.txt packages.txt .streamlit/
git commit -m "Add Streamlit web app for online access"
git push
```

### 3. Deploy to Streamlit Cloud

- Visit: <https://share.streamlit.io/>
- Connect GitHub repo
- Deploy from `streamlit_app.py`
- Get shareable URL

### 4. Share with Your Wife

Send her the URL - she can bookmark it and use it like any website!

---

## 📞 Support Resources

- **Streamlit Docs**: <https://docs.streamlit.io/>
- **Streamlit Community**: <https://discuss.streamlit.io/>
- **Deployment Guide**: <https://docs.streamlit.io/streamlit-community-cloud>

---

## 🎉 Summary

**Before:** Desktop app → Download → Install → Run locally

**After:** Visit URL → Upload → Process → Download results

✅ No installation required  
✅ Access from any device  
✅ Always up-to-date  
✅ Share with anyone via link

**Your wife can now process forms from her phone, tablet, or computer - anywhere with internet!** 🚀

---

**Made with ❤️ for easy web access**
