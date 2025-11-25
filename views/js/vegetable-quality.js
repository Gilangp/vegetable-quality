"use strict";

/**
 * @typedef {Object} Data
 * @property {string} prediction
 * @property {number} confidence
 */

/**
 * @typedef {Object} SuccessResponse
 * @property {Data} data
 */

/**
 * @typedef {Object} Error
 * @property {string} detail
 */

class Main {
  /** @type {HTMLButtonElement} */
  static button = null;
  /** @type {HTMLFormElement} */
  static form = null;
  /** @type {HTMLParagraphElement} */
  static result = null;
  /** @type {HTMLDetailsElement} */
  static details = null;
  /** @type {HTMLPreElement} */
  static summary = null;

  constructor() {
    if (new.target !== Main) {
      throw new Error("Kelas Main tidak dapat diinstansiasi.");
    }
  }

  static load() {
    document.addEventListener("DOMContentLoaded", () => {
      this.button = document.querySelector("button");
      this.form = document.querySelector("form");
      this.result = document.querySelector("p");
      this.details = document.querySelector("details");
      this.summary = document.querySelector("pre");

      if (this.form) {
        this.form.addEventListener("submit", Main.submit.bind(this));
      } else {
        console.error(`[${new Date().toISOString()}] — Form not found.`);
      }
    });
  }

  /**
   * @param {SubmitEvent} event
   * @returns {Promise<void>}
   */
  static async submit(event) {
    event.preventDefault();

    if (!this.button || !this.form || !this.result || !this.details || !this.summary) {
      console.error(`[${new Date().toISOString()}] — Form elements (button, form, result, details, summary) not found.`);
      return;
    }

    this.button.disabled = true;
    this.result.style.display = "block";
    this.result.style.color = "blue";
    this.result.textContent = "Analyzing vegetable images...";
    this.details.style.display = "none";
    this.details.open = false;
    this.summary.textContent = "";

    try {
      /** @type {Response} */
      const response = await fetch("/predict", { method: "POST", body: new FormData(this.form) });

      /** @type {Promise<SuccessResponse | Error>} */
      const data = await response.json();

      if (!response.ok) {
        /** @type {Error} */
        const error = data;
        throw new Error(error.detail || "An unknown error occurred.");
      }

      /** @type {SuccessResponse} */
      const success = data;

      console.log(`[${new Date().toISOString()}] — Image analysis successful!`);

      this.result.style.color = "green";
      this.result.textContent = "Image analysis successful!";
      this.summary.textContent = JSON.stringify(success.data, null, 2);
      this.details.style.display = "block";
    } catch (err) {
      const error = /** @type {Error} */ (err);
      console.error(`[${new Date().toISOString()}] — ${error.message}`);
      this.result.style.color = "red";
      this.result.textContent = error.message;
      this.details.style.display = "none";
    } finally {
      this.button.disabled = false;
    }
  }
}

Main.load();