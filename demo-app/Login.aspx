<%@ Page Language="C#" MasterPageFile="~/Site.master" %>

<script runat="server">
    protected void btnLogin_Click(object sender, EventArgs e)
    {
        if (txtUser.Text == "demo" && txtPass.Text == "demo123")
        {
            FormsAuthentication.RedirectFromLoginPage(txtUser.Text, false);
        }
        else
        {
            lblError.Text = "Invalid username or password.";
        }
    }
</script>
<asp:Content ContentPlaceHolderID="Main" runat="server">
    <h2 style="font-size:16px;margin-top:0;">Sign in</h2>
    <table class="dl">
        <tr>
            <th>Username</th>
            <td><asp:TextBox ID="txtUser" runat="server" /></td>
        </tr>
        <tr>
            <th>Password</th>
            <td><asp:TextBox ID="txtPass" runat="server" TextMode="Password" /></td>
        </tr>
    </table>
    <p><asp:Button ID="btnLogin" runat="server" Text="Sign in" OnClick="btnLogin_Click" /></p>
    <p style="color:#b00020;font-size:13px;">
        <asp:Label ID="lblError" runat="server" />
    </p>
    <p style="font-size:12px;color:#666;">Demo credentials: <code>demo</code> / <code>demo123</code></p>
</asp:Content>