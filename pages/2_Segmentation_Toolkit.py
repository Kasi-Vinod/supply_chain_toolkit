import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ---------------------------
# Function to perform ABC classification
# ---------------------------
def abc_classification(df, column, class_name):
    df = df.sort_values(by=column, ascending=False).reset_index(drop=True)
    df['cum_sum'] = df[column].cumsum()
    df['cum_perc'] = 100 * df['cum_sum'] / df[column].sum()

    conditions = [
        df['cum_perc'] <= 70,
        (df['cum_perc'] > 70) & (df['cum_perc'] <= 90),
        df['cum_perc'] > 90
    ]
    choices = ['A', 'B', 'C']
    df[class_name] = pd.cut(df['cum_perc'],
                            bins=[0, 70, 90, 100],
                            labels=['A', 'B', 'C'],
                            include_lowest=True).astype(str)
    return df.drop(columns=['cum_sum', 'cum_perc'])

# ---------------------------
# Streamlit App
# ---------------------------
st.title("📊 Two-Level ABC Segmentation Tool")

uploaded_file = st.file_uploader("Upload Excel file (with Item, SalesQty, Revenue columns)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Step 1: ABC by SalesQty
    df_sales = abc_classification(df.copy(), 'SalesQty', 'Sales_Class')

    # Step 2: ABC by Revenue within Sales_Class
    final_dfs = []
    for grp, data in df_sales.groupby('Sales_Class'):
        df_rev = abc_classification(data.copy(), 'Revenue', 'Revenue_Class')
        final_dfs.append(df_rev)
    df_final = pd.concat(final_dfs).sort_index()

    # Step 3: Final Class
    df_final['Final_Class'] = df_final['Sales_Class'] + "-" + df_final['Revenue_Class']

    st.success("✅ ABC Classification Completed!")

    # ---------------------------
    # Show Data
    # ---------------------------
    st.subheader("📂 Classified Data")
    st.dataframe(df_final.head(20))

    # ---------------------------
    # Summary
    # ---------------------------
    st.subheader("📈 Summary of Final Classes")
    summary = df_final['Final_Class'].value_counts().reset_index()
    summary.columns = ['Final_Class', 'Count']
    summary['Percentage'] = (summary['Count'] / summary['Count'].sum()) * 100
    st.dataframe(summary)

    # ---------------------------
    # Visualization 1: Bar Chart
    # ---------------------------
    st.subheader("📊 Distribution of Final Classes")
    chart = alt.Chart(summary).mark_bar().encode(
        x='Final_Class',
        y='Count',
        tooltip=['Final_Class', 'Count', 'Percentage']
    ).properties(width=600, height=400)
    st.altair_chart(chart)

    # ---------------------------
    # Visualization 2: Pie Chart
    # ---------------------------
    fig, ax = plt.subplots()
    ax.pie(summary['Count'], labels=summary['Final_Class'], autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # ---------------------------
    # Visualization 3: Scatter Plot
    # ---------------------------
    st.subheader("📉 SalesQty vs Revenue (colored by class)")
    scatter_chart = alt.Chart(df_final).mark_circle(size=80).encode(
        x='SalesQty',
        y='Revenue',
        color='Final_Class',
        tooltip=['Item', 'SalesQty', 'Revenue', 'Final_Class']
    ).interactive()
    st.altair_chart(scatter_chart, use_container_width=True)

    # ---------------------------
    # Download Excel
    # ---------------------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="ABC Segmentation")
        summary.to_excel(writer, index=False, sheet_name="Summary")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Classified Excel",
        data=excel_data,
        file_name="ABC_Segmentation_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------------------
    # Download PDF Report
    # ---------------------------
    def create_pdf(df_summary):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("ABC Segmentation Report", styles['Title']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("📊 Summary of Final Classes", styles['Heading2']))
        table_data = [df_summary.columns.to_list()] + df_summary.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

        story.append(Paragraph("✅ Analysis Completed Successfully.", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_report = create_pdf(summary)

    st.download_button(
        label="📑 Download PDF Report (A4)",
        data=pdf_report,
        file_name="ABC_Segmentation_Report.pdf",
        mime="application/pdf"
    )
