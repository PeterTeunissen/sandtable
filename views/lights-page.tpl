<table class="main">
  <tr>
    <td>
      <form method="post" action="lights">
        <table class="buttons">
            %r=-1
            %for num, pat in enumerate(ledPatterns):
                %p,q=divmod(num,3)
                %mr=0
                %if p!=r:
                % mr=1
                % r=p
                  <tr>
                %end
                <td valign="TOP">
                    %style = 'ledselected' if pat == pattern else 'led'
                    <button class="{{style}}" type="submit" name="method" value="{{pat}}">{{pat}}</button>
                </td>
                %p,q=divmod(num+1,3)
                %if p!=r:
                  </tr>
                %end
            %end
        </table>
      </form>
  </td>

  <td valign="TOP" style="text-align:left;">
   <h3>{{pattern}}</h3>
   <form method="post" action="lights" class="auto_submit_form">
    <input name="method" type="hidden" value="{{pattern}}">
    {{!editor}}
    <button class="doit" name="action" type="submit" value="doit">Lights!</button>
   </form>
  </td>
 </tr>
</table>

