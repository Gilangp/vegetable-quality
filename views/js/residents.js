"use strict";

/**
 * @typedef {Object} Data
 * @property {number} [id]
 * @property {number} family_id
 * @property {number} house_id
 * @property {string} nik
 * @property {string} name
 * @property {string} [phone]
 * @property {string} [birth_place]
 * @property {string} [birth_date]
 * @property {string} [gender]
 * @property {string} [status]
 * @property {string} [religion]
 * @property {string} [blood_type]
 * @property {string} [education]
 * @property {string} [occupation]
 */

class Residents {
  /** @type {Data[]} */
  residents = [];

  /** @type {string} */
  apiUrl = "/residents";

  /** @type {HTMLFormElement | null} */
  form = null;

  /** @type {HTMLTableSectionElement | null} */
  tableBody = null;

  constructor() {
    this.form = /** @type {HTMLFormElement} */ (document.getElementById("resident-form"));
    this.tableBody = /** @type {HTMLTableSectionElement} */ (document.getElementById("resident-tbody"));
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleDeleteClick = this.handleDeleteClick.bind(this);
  }

  init() {
    if (this.form) this.form.addEventListener("submit", this.handleSubmit);
    if (this.tableBody) this.tableBody.addEventListener("click", this.handleDeleteClick);
    this.get();
  }

  async get() {
    if (this.tableBody) {
      this.tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center'>Memuat data...</td></tr>";
    }

    try {
      const response = await fetch(`${this.apiUrl}/data`);
      if (!response.ok) throw new Error("Gagal mengambil data");
      this.residents = await response.json();
      this.render();
    } catch (err) {
      const error = /** @type {Error} */ (err);
      console.error(error);
      if (this.tableBody) {
        this.tableBody.innerHTML = `<tr><td colspan='7' style='text-align:center; color:red'>${error.message}</td></tr>`;
      }
    }
  }

  /**
   * @param {SubmitEvent} e
   */
  async handleSubmit(e) {
    e.preventDefault();
    if (!this.form) return;
    const formData = new FormData(this.form);

    /** @type {Data} */
    const payload = {
      family_id: 0,
      house_id: 0,
      nik: formData.get("nik")?.toString() || "",
      name: formData.get("name")?.toString() || "",
      phone: formData.get("phone")?.toString() || "",
      birth_place: formData.get("birth_place")?.toString() || "",
      birth_date: formData.get("birth_date")?.toString() || "",
      gender: formData.get("gender")?.toString() || "",
      status: formData.get("status")?.toString() || "",
      religion: formData.get("religion")?.toString() || "",
      blood_type: formData.get("blood_type")?.toString() || "",
      education: formData.get("education")?.toString() || "",
      occupation: formData.get("occupation")?.toString() || "",
    };

    await this.store(payload);
  }

  /** @param {Data} data */
  async store(data) {
    try {
      const response = await fetch(`${this.apiUrl}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Gagal menyimpan");
      }

      console.log("✅ Data tersimpan");
      if (this.form) this.form.reset();
      this.get();
    } catch (err) {
      const error = /** @type {Error} */ (err);
      alert(`Error: ${error.message}`);
    }
  }

  /** @param {MouseEvent} e */
  async handleDeleteClick(e) {
    const target = /** @type {HTMLElement} */ (e.target);

    if (target && target.classList.contains("btn-delete") && target.dataset.id) {
      await this.delete(target.dataset.id);
    }
  }

  /** @param {number|string} id */
  async delete(id) {
    if (!confirm("Yakin hapus data ini?")) return;

    try {
      const response = await fetch(`${this.apiUrl}/${id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Gagal menghapus");
      console.log("✅ Data terhapus");
      this.get();
    } catch (err) {
      const error = /** @type {Error} */ (err);
      alert(`Error: ${error.message}`);
    }
  }

  render() {
    if (!this.tableBody) return;
    this.tableBody.innerHTML = "";

    if (this.residents.length === 0) {
      this.tableBody.innerHTML = "<tr><td colspan='7' style='text-align:center'>Tidak ada data</td></tr>";
      return;
    }

    this.residents.forEach((item) => {
      const row = `
        <tr>
          <td>${item.nik}</td>
          <td>${item.name}</td>
          <td>${item.gender}</td>
          <td>${item.phone || "-"}</td>
          <td>${item.birth_place || ""}, ${item.birth_date || ""}</td>
          <td>${item.status}</td>
          <td>
            <button class="btn-delete" data-id="${item.id}">Hapus</button>
          </td>
        </tr>
      `;

      this.tableBody.insertAdjacentHTML("beforeend", row);
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new Residents().init();
});