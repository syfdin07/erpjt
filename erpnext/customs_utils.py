import frappe

REPORTS = [
    "Laporan Pemasukan Barang",
    "Laporan Pengeluaran Barang",
    "Laporan Posisi WIP",
    "Laporan Mutasi Bahan Baku/ Bahan Penolong",
    "Laporan Mutasi Barang Jadi",
    "Laporan Mutasi Mesin dan Peralatan",
    "Laporan Barang Reject dan Scrap",
]

OLD_REPORTS = [
    "Laporan Pemasukan Barang Per Dokumen Pabean",
    "Laporan Pengeluaran Barang Per Dokumen Pabean",
    "Laporan Posisi WIP",
    "Laporan Pertanggungjawaban Mutasi Bahan Baku/ Bahan Penolong",
    "Laporan Pertanggungjawaban Mutasi Barang Jadi",
    "Laporan Pertanggungjawaban Mutasi Mesin dan Peralatan",
    "Laporan Pertanggungjawaban Barang Reject dan Scrap",
]

def rename_customs_reports():
    renamed = []
    for old, new in zip(OLD_REPORTS, REPORTS):
        if old == new:
            continue
        if frappe.db.exists("Report", old):
            frappe.rename_doc("Report", old, new, force=True)
            renamed.append((old, new))

    ws = frappe.get_doc("Workspace", "Customs")
    for link in ws.links:
        for old, new in renamed:
            if link.label == old:
                link.label = new
                link.link_to = new
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    return {"renamed": renamed}

def make_customs_reports_and_menu():
    created = []
    for rpt in REPORTS:
        if frappe.db.exists("Report", rpt):
            continue
        doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": rpt,
            "ref_doctype": "Stock Ledger Entry",
            "report_type": "Query Report",
            "module": "Customs",
            "is_standard": "No",
            "query": "-- TODO: implement query\nSELECT name, posting_date, item_code, warehouse, actual_qty\nFROM `tabStock Ledger Entry`\nLIMIT 10",
        })
        doc.insert(ignore_permissions=True)
        created.append(rpt)

    ws = frappe.get_doc("Workspace", "Customs")
    existing = {l.label for l in ws.links}
    for rpt in REPORTS:
        if rpt not in existing:
            ws.append("links", {
                "type": "Link",
                "label": rpt,
                "link_type": "Report",
                "link_to": rpt,
            })
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    return {"reports_created": created, "workspace_links": len(ws.links)}
