// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCOEf3vUGonpB14apXCcR3_qRVRz1aZdv0",
  authDomain: "feedback-cot.firebaseapp.com",
  projectId: "feedback-cot",
  storageBucket: "feedback-cot.firebasestorage.app",
  messagingSenderId: "949280164854",
  appId: "1:949280164854:web:a9225f6921dc7cdf4955d7",
  measurementId: "G-NSLM8GJEWJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);