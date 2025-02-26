# 📌 iChooseRx Pull Request Template

## **🔹 Summary**
<!-- Briefly describe what this PR does. What problem does it solve? -->

## **🔹 Changes Implemented**
<!-- List key updates and features added in this PR -->
- ✅ Feature 1
- ✅ Feature 2
- ✅ Bug Fixes
- ✅ Code refactoring / performance improvements

## **🔹 Services Affected**
<!-- Mark all relevant services affected -->
- [ ] 🚀 **Rails Backend**
- [ ] 🐍 **Python Microservice**
- [ ] ⚡ **Next.js Frontend**
- [ ] 📦 **Database**
- [ ] 📂 **File Processing**
- [ ] 🔄 **CI/CD Pipelines**
- [ ] 🔐 **Security & RBAC**
- [ ] 📊 **Admin Dashboard**
- [ ] 🏥 **Pharmacy Dashboard**
- [ ] 👤 **User Dashboard**

## **🔹 How to Test**
<!-- Step-by-step instructions to verify this PR works as expected -->
1️⃣ **Pull the latest changes**:  
   ```sh
   git checkout <your-branch> && git pull
   ```
2️⃣ **Run migrations (if applicable)**:  
   ```sh
   rails db:migrate
   ```
3️⃣ **Run the application on local server http://localhost:3000/signup OR /login OR /dashboard (if already logged)**:  
   ```sh
   rails s  # Backend (runs on http://localhost:5001)
   npm run dev  # Next.js frontend (Runs on http://localhost:3000)
   python main.py  # Python microservice
   python watch_pharmacy_data.py # (Optional) If using the microservice file watcher:
   ```

4️⃣ **(Only for Microservice) Virtual Environment Setup**
   ```sh
   # Create Virtual Environment (Only If Not Already Created)
   python -m venv venv  

   # Activate Virtual Environment if not already activated (BEFORE running Python scripts)
   source venv/bin/activate  # macOS/Linux  
   venv\Scripts\activate  # Windows Command Prompt  
   venv\Scripts\Activate.ps1  # Windows PowerShell  

   # Run Watchdog Service (For Pharmacy File Uploads)
   python watch_pharmacy_data.py  

   # Deactivate Virtual Environment (When Done)
   deactivate  

   # Remove Virtual Environment (If Needed)
   rm -rf venv  # macOS/Linux  
   rd /s /q venv  # Windows Command Prompt  
   ```
5️⃣ **Test the feature / bug fix** 
6️⃣ **Check logs for errors**  
7️⃣ **Verify database updates (if applicable)** 

## **🔹 Did Anything Break?**
- [ ] 🚨 **Yes** (explain below)
- [ ] ✅ **No**
- 🔍 **Describe any breaking changes:**  
  <!-- If something broke, what was it? What’s the impact? -->

## **🔹 Did This Fix Something That Was Not Working Before?**
- [ ] ✅ **Yes**  
  - 🔧 **Describe the issue that was fixed:**  
  <!-- Example: "Fixed an issue where NDC data was not saving correctly" -->
- [ ] ❌ **No**

## **🔹 Screenshots / Logs (Optional)**
<!-- Add relevant screenshots or log snippets if applicable -->

## **🔹 Does This Introduce Database Migrations?**
- [ ] 🔄 **Yes** (run `rails db:migrate`)
- [ ] ✅ **No**

## **🔹 Related Issues / PRs**
<!-- Link any related issues or PRs -->
- Closes #ISSUE_NUMBER
- Related PR: #OTHER_PR

## **🔹 Checklist Before Merging**
- [ ] ✅ PR has been tested locally
- [ ] ✅ Tests pass (`rspec`, `pytest`, `jest`, etc.)
- [ ] ✅ No console errors or warnings
- [ ] ✅ Code follows DRY & SRP principles
- [ ] ✅ Code has been reviewed

---

### **📌 Notes**
<!-- Any additional information for reviewers? -->
