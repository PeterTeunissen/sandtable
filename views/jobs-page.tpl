<table class="main">
  <tr>
    <td valign="TOP">
      <form method="post" action="jobs">
        <table cellspacing="1px" cellpadding="5px" border="1">          
          <tr>
           <th>ID</th>
           <th>Name</th>
           <th>Function</th>
           <th>Args</th>
           <th>Schedule</th>
           <th>Next Run Time</th>
           <th>&nbsp;</th>
           <th>&nbsp;</th>
          </tr>
            %for num, job in enumerate(jobs):
              <tr>
                <td>
                   {{job['id']}}
                </td>
                <td>
                  {{job['name']}}
                </td>
                <td>
                  {{job['function']}}
                </td>
                <td>
                  {{job['args']}}
                </td>
                <td>
                  {{job['trigger']}}
               </td>
                <td>
                  {{job['next_run_time']}}
               </td>
               <td>
                    <form method="post" action="jobs">
                    <input  type="hidden" name="deleteId" value="{{job['id']}}" />
                    <button  type="submit" name="action" value="delete">Delete</button>
                    </form>
               </td>
               <td>
                    <form method="post" action="jobs">
                    <input  type="hidden" name="jobId" value="{{job['id']}}" />
                    <button  type="submit" name="action" value="runNow">Run Now</button>
                    </form>
               </td>
              </tr>
            %end
        </table>
      </form>
  </td>

  <td valign="TOP" style="text-align:left;">
   <form method="post" action="jobs" class="auto_submit_form">
    <input name="method" type="hidden" value="">
    {{!editor}}
    <span class="navigation"><a href="cronhelp" target="sand_help">Cron help.</a></span>    
    <br>
    <button class="doit" name="action" type="submit" value="add">Add</button>
    </form>
   </td>
  </td>
 </tr>
</table>

