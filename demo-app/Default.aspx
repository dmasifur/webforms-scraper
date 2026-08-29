<%@ Page Language="C#" MasterPageFile="~/Site.master" %>
<%-- 
     Three distinct postback shapes live on this page:
       1. ddlCampus  -> AutoPostBack, __EVENTTARGET only
       2. pager      -> __EVENTTARGET + __EVENTARGUMENT ("Page$3")
       3. lnkDetail  -> generated target (gvStudents$ctl03$lnkDetail), shifts on rebind --%>
<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            ddlCampus.DataSource = StudentData.Campuses();
            ddlCampus.DataBind();
            ddlCampus.Items.Insert(0, new ListItem("All campuses", ""));
            BindGrid();
        }
    }

    private void BindGrid()
    {
        System.Collections.Generic.List<Student> rows =
            StudentData.Query(ddlCampus.SelectedValue);
        gvStudents.DataSource = rows;
        gvStudents.DataBind();
        lblCount.Text = rows.Count.ToString() + " record(s)";
    }

    protected void ddlCampus_SelectedIndexChanged(object sender, EventArgs e)
    {
        gvStudents.PageIndex = 0;
        BindGrid();
    }

    protected void gvStudents_PageIndexChanging(object sender, GridViewPageEventArgs e)
    {
        gvStudents.PageIndex = e.NewPageIndex;
        BindGrid();
    }

    protected void gvStudents_RowCommand(object sender, GridViewCommandEventArgs e)
    {
        if (e.CommandName == "ViewDetail")
        {
            Session["SelectedStudentId"] = Convert.ToString(e.CommandArgument);
            Response.Redirect("~/Details.aspx");
        }
    }
</script>
<asp:Content ContentPlaceHolderID="Main" runat="server">
    <h2 style="font-size:16px;margin-top:0;">Student Register</h2>

    <div class="toolbar">
        Campus:
        <asp:DropDownList ID="ddlCampus" runat="server"
                          AutoPostBack="true"
                          OnSelectedIndexChanged="ddlCampus_SelectedIndexChanged" />
        &nbsp;&nbsp;
        <asp:Label ID="lblCount" runat="server" ForeColor="#666" />
    </div>

    <asp:GridView ID="gvStudents" runat="server"
                  AutoGenerateColumns="false"
                  AllowPaging="true"
                  PageSize="20"
                  CssClass="grid"
                  GridLines="None"
                  OnPageIndexChanging="gvStudents_PageIndexChanging"
                  OnRowCommand="gvStudents_RowCommand">
        <PagerStyle CssClass="pager" />
        <Columns>
            <asp:BoundField DataField="StudentId" HeaderText="Student ID" />
            <asp:BoundField DataField="FullName"  HeaderText="Name" />
            <asp:BoundField DataField="Campus"    HeaderText="Campus" />
            <asp:BoundField DataField="Course"    HeaderText="Course" />
            <asp:BoundField DataField="EnrolmentDate" HeaderText="Enrolled"
                            DataFormatString="{0:dd/MM/yyyy}" HtmlEncode="false" />
            <asp:BoundField DataField="Status"    HeaderText="Status" />
            <asp:TemplateField HeaderText="">
                <ItemTemplate>
                    <asp:LinkButton ID="lnkDetail" runat="server"
                                    CommandName="ViewDetail"
                                    CommandArgument='<%# Eval("StudentId") %>'
                                    Text="View" />
                </ItemTemplate>
            </asp:TemplateField>
        </Columns>
    </asp:GridView>
</asp:Content>