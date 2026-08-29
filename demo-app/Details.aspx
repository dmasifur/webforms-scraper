<%@ Page Language="C#" MasterPageFile="~/Site.master" %>
<%-- 
     No query string. The record identity comes from Session, so this page cannot
     be enumerated — the scraper must replay the grid postback to reach each record. --%>
<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {
        if (IsPostBack) { return; }

        object id = Session["SelectedStudentId"];
        if (id == null)
        {
            Response.Redirect("~/Default.aspx");
            return;
        }

        Student s = StudentData.Find(Convert.ToString(id));
        if (s == null)
        {
            Response.Redirect("~/Default.aspx");
            return;
        }

        litStudentId.Text = Server.HtmlEncode(s.StudentId);
        litName.Text = Server.HtmlEncode(s.FullName);
        litEmail.Text = Server.HtmlEncode(s.Email);
        litPhone.Text = Server.HtmlEncode(s.Phone);
        litDob.Text = s.DateOfBirth.ToString("dd/MM/yyyy");
        litAddress.Text = Server.HtmlEncode(s.Address);
        litEmergency.Text = Server.HtmlEncode(s.EmergencyContact);
        litCourse.Text = Server.HtmlEncode(s.Course);
        litCampus.Text = Server.HtmlEncode(s.Campus);
        litStatus.Text = Server.HtmlEncode(s.Status);
        litEnrolled.Text = s.EnrolmentDate.ToString("dd/MM/yyyy");
    }

    protected void lnkBack_Click(object sender, EventArgs e)
    {
        Response.Redirect("~/Default.aspx");
    }
</script>
<asp:Content ContentPlaceHolderID="Main" runat="server">
    <h2 style="font-size:16px;margin-top:0;">Student Detail</h2>

    <table class="dl" id="tblDetail">
        <tr><th>Student ID</th><td id="tdStudentId"><asp:Literal ID="litStudentId" runat="server" /></td></tr>
        <tr><th>Name</th><td id="tdName"><asp:Literal ID="litName" runat="server" /></td></tr>
        <tr><th>Campus</th><td id="tdCampus"><asp:Literal ID="litCampus" runat="server" /></td></tr>
        <tr><th>Course</th><td id="tdCourse"><asp:Literal ID="litCourse" runat="server" /></td></tr>
        <tr><th>Status</th><td id="tdStatus"><asp:Literal ID="litStatus" runat="server" /></td></tr>
        <tr><th>Enrolment Date</th><td id="tdEnrolled"><asp:Literal ID="litEnrolled" runat="server" /></td></tr>
        <tr><th>Email</th><td id="tdEmail"><asp:Literal ID="litEmail" runat="server" /></td></tr>
        <tr><th>Phone</th><td id="tdPhone"><asp:Literal ID="litPhone" runat="server" /></td></tr>
        <tr><th>Date of Birth</th><td id="tdDob"><asp:Literal ID="litDob" runat="server" /></td></tr>
        <tr><th>Address</th><td id="tdAddress"><asp:Literal ID="litAddress" runat="server" /></td></tr>
        <tr><th>Emergency Contact</th><td id="tdEmergency"><asp:Literal ID="litEmergency" runat="server" /></td></tr>
    </table>

    <p style="margin-top:18px;">
        <asp:LinkButton ID="lnkBack" runat="server" Text="&laquo; Back to register"
                        OnClick="lnkBack_Click" />
    </p>
</asp:Content>