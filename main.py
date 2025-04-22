# Example of using the Phase 1 chains
from chains.issue_understanding import summarize_issue
from chains.file_selector import predict_files_for_issue

repo_name = "octocat/Hello-World"    # replace with your target repo
issue_num = 42                       # replace with the issue number of interest

# Step 1: Get issue summary
summary = summarize_issue(repo_name, issue_num)
print("Issue Summary:\n", summary)

# Step 2: Predict relevant files based on the summary
files_prediction = predict_files_for_issue(summary, repo_name)
print("\nPredicted Files to Modify:\n", files_prediction)